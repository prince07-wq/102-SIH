"""
services/project_service.py
============================
Data-access and schema-adaptation layer for processed MPLADS project records.

The service reads the API-ready output produced by the offline intelligence
pipeline. Routes do not access pipeline JSON directly, and this module does
not calculate or modify anomaly scores.
"""

import csv
import io
import re
import unicodedata
from functools import lru_cache
from typing import Iterator, List, Optional

from app.db import get_connection

from app.schemas.project import (
    AlertRecord,
    AlertsResponse,
    ProjectAggregatesResponse,
    ProjectFilterOptions,
    ProjectListResponse,
    ProjectRecord,
    StatisticsResponse,
)
from app.services.search_config import (
    MIN_PARTIAL_TOKEN_LENGTH,
    SEARCH_ALIAS_GROUPS,
)

_RISK_COMPONENTS = ["cost", "delay", "expenditure", "duplicate"]


def _to_vendor_record(vendor):
    """Converts one snake_case vendor entry to the public API shape."""
    vendor_id = vendor.get("vendor_id")
    return {
        "vendorId": str(vendor_id) if vendor_id is not None else None,
        "vendorName": vendor.get("vendor_name"),
    }


def _to_similar_project(record):
    """Converts detector-provided similar-project evidence without rescoring it."""
    return {
        "projectId": str(record.get("project_id")),
        "workName": record.get("work_description") or "",
        "sanctionAmount": record.get("sanction_amount"),
        "sanctionDate": record.get("sanction_date"),
        "dateDifferenceDays": record.get("date_difference_days"),
        "similarity": None,
    }


def _to_project_record(record):
    """Adapts one pipeline record to the existing camelCase API contract."""
    vendors = [
        _to_vendor_record(vendor)
        for vendor in record.get("vendors", [])
        if isinstance(vendor, dict)
    ]
    vendor_name = vendors[0]["vendorName"] if vendors else None

    flag_count = record.get("flag_count") or 0

    risk = {
        "overallScore": record.get("overall_score"),
        "level": record.get("risk_level"),
        "flagCount": flag_count,
        "baseScore": record.get("base_score"),
        "strongestDetector": record.get("strongest_detector"),
        "multiSignalBonus": record.get("multi_signal_bonus"),
        "scoreCapped": record.get("score_capped"),
    }
    for component_name in _RISK_COMPONENTS:
        risk[component_name] = record.get(component_name)

    return ProjectRecord(
        projectId=str(record.get("project_id")),
        workName=record.get("work_description") or record.get("activity_name") or "",
        activityName=record.get("activity_name"),
        description=record.get("work_description"),
        category=record.get("work_category"),
        state=record.get("state_name"),
        constituency=record.get("constituency"),
        mpName=record.get("mp_name"),
        authority=record.get("ida_name"),
        recommendationDate=record.get("recommendation_date"),
        sanctionDate=record.get("sanction_date"),
        sanctionAmount=record.get("sanction_amount"),
        workStage=record.get("work_stage"),
        vendorName=vendor_name,
        totalDisbursed=record.get("total_disbursed"),
        lastExpenditureDate=record.get("last_expenditure_date"),
        tenure=record.get("tenure"),
        houseOfParliament=record.get("house_of_parliament"),
        hasExpenditure=record.get("has_expenditure"),
        expenditureRecordCount=record.get("expenditure_record_count"),
        uniqueVendorCount=record.get("unique_vendor_count"),
        firstExpenditureDate=record.get("first_expenditure_date"),
        vendors=vendors,
        workIds=[str(work_id) for work_id in record.get("work_ids", [])],
        officialWorkIds=[
            int(work_id) for work_id in record.get("official_work_ids", [])
        ],
        hasOfficialAttachment=record.get("has_official_attachment", False),
        mlEligible=record.get("ml_eligible"),
        mlStatus=record.get("ml_status"),
        mlRawScore=record.get("ml_raw_score"),
        mlAnomalyValue=record.get("ml_anomaly_value"),
        mlAnomalyScore=record.get("ml_anomaly_score"),
        mlIsAnomaly=record.get("ml_is_anomaly"),
        mlAnomalyLevel=record.get("ml_anomaly_level"),
        mlRuleAgreement=record.get("ml_rule_agreement"),
        mlProjectAgeDays=record.get("ml_project_age_days"),
        mlDaysToFirstExpenditure=record.get(
            "ml_days_to_first_expenditure"
        ),
        mlExpenditureRecordCount=record.get(
            "ml_expenditure_record_count"
        ),
        mlUniqueVendorCount=record.get("ml_unique_vendor_count"),
        mlDisbursementRatio=record.get("ml_disbursement_ratio"),
        mlWorkStage=record.get("ml_work_stage"),
        risk=risk,
        similarProjects=[
            _to_similar_project(similar)
            for similar in record.get("similar_projects", [])
            if isinstance(similar, dict)
        ],
    )


def _risk_filter_value(risk):
    """Maps the legacy MEDIUM filter name to Combined Risk V1 MODERATE."""
    if risk is None:
        return None
    normalized = risk.strip().upper()
    return "MODERATE" if normalized == "MEDIUM" else normalized


def _page_count(total, page_size):
    """Returns the number of pages for a result count and page size."""
    return (total + page_size - 1) // page_size


def _normalize_search_text(value):
    """Normalizes case, accents, punctuation, and whitespace for search."""
    normalized = unicodedata.normalize("NFKD", str(value or "").casefold())
    normalized = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(re.sub(r"[^\w]+", " ", normalized).split())


def _token_matches(query_token, document_token):
    """Matches exact tokens and document words that extend a typed prefix."""
    if query_token == document_token:
        return True
    if min(len(query_token), len(document_token)) < MIN_PARTIAL_TOKEN_LENGTH:
        return False
    return document_token.startswith(query_token)


def _variant_matches(tokens, variant):
    """Checks whether every word in an alias variant occurs in any order."""
    return all(
        any(_token_matches(query_token, token) for token in tokens)
        for query_token in variant
    )


def _find_query_variant(query_tokens, aliases):
    """Finds the longest alias phrase represented by query tokens."""
    candidates = []
    for alias in aliases:
        alias_tokens = tuple(_normalize_search_text(alias).split())
        if len(alias_tokens) <= len(query_tokens) and _variant_matches(
            query_tokens, alias_tokens
        ):
            candidates.append(alias_tokens)
    return max(candidates, key=len, default=None)


def _remove_matched_tokens(query_tokens, matched_tokens):
    """Removes one query token for each word consumed by an alias concept."""
    remaining = list(query_tokens)
    for matched_token in matched_tokens:
        for index, query_token in enumerate(remaining):
            if _token_matches(matched_token, query_token):
                remaining.pop(index)
                break
    return remaining


def _query_groups(search_value):
    """Builds ANDed query concepts with ORed layman/synonym variants."""
    remaining_tokens = search_value.split()
    groups = []

    for aliases in SEARCH_ALIAS_GROUPS.values():
        matched_variant = _find_query_variant(remaining_tokens, aliases)
        if not matched_variant:
            continue
        groups.append(
            tuple(tuple(_normalize_search_text(alias).split()) for alias in aliases)
        )
        remaining_tokens = _remove_matched_tokens(
            remaining_tokens, matched_variant
        )

    groups.extend(((token,),) for token in remaining_tokens)
    return tuple(groups)


def _db_record(row):
    """Converts a PostgreSQL row back to the pipeline-record shape."""
    record = dict(row)

    details = record.pop("details", None) or {}
    record.update(details)

    for field_name in (
        "recommendation_date",
        "sanction_date",
        "first_expenditure_date",
        "last_expenditure_date",
    ):
        value = record.get(field_name)
        if value is not None and hasattr(value, "isoformat"):
            record[field_name] = value.isoformat()

    return record

def get_all_projects(
    risk: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    ml_eligible: Optional[bool] = None,
    ml_is_anomaly: Optional[bool] = None,
    ml_anomaly_level: Optional[str] = None,
    ml_rule_agreement: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> ProjectListResponse:

    conditions = []
    params = []

    if risk:
        conditions.append("risk_level = %s")
        params.append(_risk_filter_value(risk))

    if state:
        conditions.append("state_name ILIKE %s")
        params.append(f"%{state.strip()}%")

    if category:
        conditions.append("LOWER(work_category) = LOWER(%s)")
        params.append(category.strip())

    if ml_eligible is not None:
        conditions.append("ml_eligible = %s")
        params.append(ml_eligible)

    if ml_is_anomaly is not None:
        conditions.append("ml_is_anomaly = %s")
        params.append(ml_is_anomaly)

    if ml_anomaly_level:
        conditions.append("ml_anomaly_level = %s")
        params.append(ml_anomaly_level.strip().upper())

    if ml_rule_agreement:
        conditions.append("ml_rule_agreement = %s")
        params.append(ml_rule_agreement.strip().upper())

    # Must NOT be inside the ml_rule_agreement block.
    search_order = ""
    order_params = []

    if search and search.strip():
        search_value = _normalize_search_text(search)

        searchable_columns = (
            "work_description",
            "activity_name",
            "state_name",
            "constituency",
            "mp_name",
            "ida_name",
            "vendor_names",
            "work_ids_text",
        )

        groups = _query_groups(search_value)

        search_sql_parts = []
        search_params = []

        for group in groups:
            variant_sql_parts = []

            # Alternatives/synonyms inside a group are OR.
            for variant in group:
                token_sql_parts = []

                # Tokens inside one variant are AND,
                # but each token may match any searchable column.
                for token in variant:
                    field_checks = []

                    for column in searchable_columns:
                        field_checks.append(f"{column} ILIKE %s")
                        search_params.append(f"%{token}%")

                    token_sql_parts.append(
                        "(" + " OR ".join(field_checks) + ")"
                    )

                if token_sql_parts:
                    variant_sql_parts.append(
                        "(" + " AND ".join(token_sql_parts) + ")"
                    )

            if variant_sql_parts:
                search_sql_parts.append(
                    "(" + " OR ".join(variant_sql_parts) + ")"
                )

        if search_sql_parts:
            search_expression = " AND ".join(search_sql_parts)

            if search_value.isdigit():
                conditions.append(
                    f"(project_id = %s OR ({search_expression}))"
                )

                params.append(int(search_value))
                params.extend(search_params)

                search_order = (
                    "CASE WHEN project_id = %s THEN 0 ELSE 1 END,"
                )
                order_params.append(int(search_value))

            else:
                conditions.append(f"({search_expression})")
                params.extend(search_params)

        elif search_value.isdigit():
            # Defensive fallback for exact project-ID search.
            conditions.append("project_id = %s")
            params.append(int(search_value))

            search_order = (
                "CASE WHEN project_id = %s THEN 0 ELSE 1 END,"
            )
            order_params.append(int(search_value))

    where_sql = (
        "WHERE " + " AND ".join(conditions)
        if conditions
        else ""
    )

    offset = (page - 1) * page_size

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM projects
                {where_sql}
                """,
                params,
            )

            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT *
                FROM projects
                {where_sql}
                ORDER BY
                    {search_order}
                    project_id
                LIMIT %s OFFSET %s
                """,
                params + order_params + [page_size, offset],
            )

            rows = cur.fetchall()

    projects = [
        _to_project_record(_db_record(row))
        for row in rows
    ]

    return ProjectListResponse(
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=_page_count(total, page_size),
        projects=projects,
    )


def iter_project_export(
    risk: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    ml_eligible: Optional[bool] = None,
    ml_is_anomaly: Optional[bool] = None,
    ml_anomaly_level: Optional[str] = None,
    ml_rule_agreement: Optional[str] = None,
) -> Iterator[str]:
    """Streams a filtered CSV export directly from PostgreSQL."""

    field_names = [
        "project_id",
        "work_name",
        "state",
        "constituency",
        "mp_name",
        "authority",
        "category",
        "sanction_amount",
        "total_expenditure",
        "risk_level",
        "overall_score",
        "flag_count",
        "cost_flagged",
        "delay_flagged",
        "expenditure_flagged",
        "duplicate_flagged",
    ]

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=field_names,
        lineterminator="\n",
    )

    writer.writeheader()
    yield buffer.getvalue()

    conditions = []
    params = []

    if risk:
        conditions.append("risk_level = %s")
        params.append(_risk_filter_value(risk))

    if state:
        conditions.append("state_name ILIKE %s")
        params.append(f"%{state.strip()}%")

    if category:
        conditions.append("LOWER(work_category) = LOWER(%s)")
        params.append(category.strip())

    if ml_eligible is not None:
        conditions.append("ml_eligible = %s")
        params.append(ml_eligible)

    if ml_is_anomaly is not None:
        conditions.append("ml_is_anomaly = %s")
        params.append(ml_is_anomaly)

    if ml_anomaly_level:
        conditions.append("ml_anomaly_level = %s")
        params.append(ml_anomaly_level.strip().upper())

    if ml_rule_agreement:
        conditions.append("ml_rule_agreement = %s")
        params.append(ml_rule_agreement.strip().upper())

    # Keep export search semantics identical to project list/aggregates.
    if search and search.strip():
        search_value = _normalize_search_text(search)

        searchable_columns = (
            "work_description",
            "activity_name",
            "state_name",
            "constituency",
            "mp_name",
            "ida_name",
            "vendor_names",
            "work_ids_text",
        )

        groups = _query_groups(search_value)

        search_sql_parts = []
        search_params = []

        for group in groups:
            variant_sql_parts = []

            for variant in group:
                token_sql_parts = []

                for token in variant:
                    field_checks = []

                    for column in searchable_columns:
                        field_checks.append(f"{column} ILIKE %s")
                        search_params.append(f"%{token}%")

                    token_sql_parts.append(
                        "(" + " OR ".join(field_checks) + ")"
                    )

                if token_sql_parts:
                    variant_sql_parts.append(
                        "(" + " AND ".join(token_sql_parts) + ")"
                    )

            if variant_sql_parts:
                search_sql_parts.append(
                    "(" + " OR ".join(variant_sql_parts) + ")"
                )

        if search_sql_parts:
            search_expression = " AND ".join(search_sql_parts)

            if search_value.isdigit():
                conditions.append(
                    f"(project_id = %s OR ({search_expression}))"
                )
                params.append(int(search_value))
                params.extend(search_params)
            else:
                conditions.append(f"({search_expression})")
                params.extend(search_params)

        elif search_value.isdigit():
            conditions.append("project_id = %s")
            params.append(int(search_value))

    where_sql = (
        "WHERE " + " AND ".join(conditions)
        if conditions
        else ""
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    project_id,
                    work_description,
                    activity_name,
                    state_name,
                    constituency,
                    mp_name,
                    ida_name,
                    work_category,
                    sanction_amount,
                    total_disbursed,
                    risk_level,
                    overall_score,
                    flag_count,

                    COALESCE(
                        (details->'cost'->>'flagged')::boolean,
                        FALSE
                    ) AS cost_flagged,

                    COALESCE(
                        (details->'delay'->>'flagged')::boolean,
                        FALSE
                    ) AS delay_flagged,

                    COALESCE(
                        (details->'expenditure'->>'flagged')::boolean,
                        FALSE
                    ) AS expenditure_flagged,

                    COALESCE(
                        (details->'duplicate'->>'flagged')::boolean,
                        FALSE
                    ) AS duplicate_flagged

                FROM projects
                {where_sql}
                ORDER BY project_id
                """,
                params,
            )

            # fetchmany avoids loading the entire export into Python memory.
            while True:
                rows = cur.fetchmany(1000)

                if not rows:
                    break

                for row in rows:
                    buffer.seek(0)
                    buffer.truncate(0)

                    writer.writerow(
                        {
                            "project_id": row["project_id"],
                            "work_name": (
                                row["work_description"]
                                or row["activity_name"]
                            ),
                            "state": row["state_name"],
                            "constituency": row["constituency"],
                            "mp_name": row["mp_name"],
                            "authority": row["ida_name"],
                            "category": row["work_category"],
                            "sanction_amount": row["sanction_amount"],
                            "total_expenditure": row["total_disbursed"],
                            "risk_level": row["risk_level"],
                            "overall_score": row["overall_score"],
                            "flag_count": row["flag_count"],
                            "cost_flagged": row["cost_flagged"],
                            "delay_flagged": row["delay_flagged"],
                            "expenditure_flagged": row["expenditure_flagged"],
                            "duplicate_flagged": row["duplicate_flagged"],
                        }
                    )

                    yield buffer.getvalue()


@lru_cache(maxsize=128)
def get_project_aggregates(
    risk: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    ml_eligible: Optional[bool] = None,
    ml_is_anomaly: Optional[bool] = None,
    ml_anomaly_level: Optional[str] = None,
    ml_rule_agreement: Optional[str] = None,
) -> ProjectAggregatesResponse:
    """Aggregates the complete filtered PostgreSQL result set."""

    conditions = []
    params = []

    if risk:
        conditions.append("risk_level = %s")
        params.append(_risk_filter_value(risk))

    if state:
        conditions.append("state_name ILIKE %s")
        params.append(f"%{state.strip()}%")

    if category:
        conditions.append("LOWER(work_category) = LOWER(%s)")
        params.append(category.strip())

    if ml_eligible is not None:
        conditions.append("ml_eligible = %s")
        params.append(ml_eligible)

    if ml_is_anomaly is not None:
        conditions.append("ml_is_anomaly = %s")
        params.append(ml_is_anomaly)

    if ml_anomaly_level:
        conditions.append("ml_anomaly_level = %s")
        params.append(ml_anomaly_level.strip().upper())

    if ml_rule_agreement:
        conditions.append("ml_rule_agreement = %s")
        params.append(ml_rule_agreement.strip().upper())

    # Preserve the exact same search behavior as get_all_projects().
    if search and search.strip():
        search_value = _normalize_search_text(search)

        searchable_columns = (
            "work_description",
            "activity_name",
            "state_name",
            "constituency",
            "mp_name",
            "ida_name",
            "vendor_names",
            "work_ids_text",
        )

        groups = _query_groups(search_value)

        search_sql_parts = []
        search_params = []

        for group in groups:
            variant_sql_parts = []

            for variant in group:
                token_sql_parts = []

                for token in variant:
                    field_checks = []

                    for column in searchable_columns:
                        field_checks.append(f"{column} ILIKE %s")
                        search_params.append(f"%{token}%")

                    token_sql_parts.append(
                        "(" + " OR ".join(field_checks) + ")"
                    )

                if token_sql_parts:
                    variant_sql_parts.append(
                        "(" + " AND ".join(token_sql_parts) + ")"
                    )

            if variant_sql_parts:
                search_sql_parts.append(
                    "(" + " OR ".join(variant_sql_parts) + ")"
                )

        if search_sql_parts:
            search_expression = " AND ".join(search_sql_parts)

            if search_value.isdigit():
                conditions.append(
                    f"(project_id = %s OR ({search_expression}))"
                )
                params.append(int(search_value))
                params.extend(search_params)

            else:
                conditions.append(f"({search_expression})")
                params.extend(search_params)

        elif search_value.isdigit():
            conditions.append("project_id = %s")
            params.append(int(search_value))

    where_sql = (
        "WHERE " + " AND ".join(conditions)
        if conditions
        else ""
    )

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Overall aggregate statistics.
            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS total_projects,

                    COALESCE(SUM(sanction_amount), 0) AS total_sanction_amount,
                    COALESCE(SUM(total_disbursed), 0) AS total_expenditure,

                    COUNT(*) FILTER (
                        WHERE risk_level = 'LOW'
                    ) AS low_count,

                    COUNT(*) FILTER (
                        WHERE risk_level = 'MODERATE'
                    ) AS moderate_count,

                    COUNT(*) FILTER (
                        WHERE risk_level = 'HIGH'
                    ) AS high_count,

                    COUNT(*) FILTER (
                        WHERE risk_level = 'CRITICAL'
                    ) AS critical_count,

                    COUNT(*) FILTER (
                        WHERE
                            COALESCE(
                                (details->'cost'->>'flagged')::boolean,
                                FALSE
                            )
                            OR COALESCE(
                                (details->'delay'->>'flagged')::boolean,
                                FALSE
                            )
                            OR COALESCE(
                                (details->'expenditure'->>'flagged')::boolean,
                                FALSE
                            )
                            OR COALESCE(
                                (details->'duplicate'->>'flagged')::boolean,
                                FALSE
                            )
                    ) AS requires_review_count,

                    COUNT(*) FILTER (
                        WHERE COALESCE(
                            (details->'cost'->>'flagged')::boolean,
                            FALSE
                        )
                    ) AS cost_flagged,

                    COUNT(*) FILTER (
                        WHERE COALESCE(
                            (details->'delay'->>'flagged')::boolean,
                            FALSE
                        )
                    ) AS delay_flagged,

                    COUNT(*) FILTER (
                        WHERE COALESCE(
                            (details->'expenditure'->>'flagged')::boolean,
                            FALSE
                        )
                    ) AS expenditure_flagged,

                    COUNT(*) FILTER (
                        WHERE COALESCE(
                            (details->'duplicate'->>'flagged')::boolean,
                            FALSE
                        )
                    ) AS duplicate_flagged,

                    COUNT(*) FILTER (
                        WHERE ml_eligible IS TRUE
                    ) AS ml_eligible_count,

                    COUNT(*) FILTER (
                        WHERE ml_is_anomaly IS TRUE
                    ) AS ml_anomaly_count,

                    COUNT(*) FILTER (
                        WHERE ml_status = 'ML_NOT_APPLICABLE'
                    ) AS ml_not_applicable_count,

                    COUNT(*) FILTER (
                        WHERE ml_rule_agreement = 'ML_ONLY'
                    ) AS ml_only_count,

                    COUNT(*) FILTER (
                        WHERE ml_rule_agreement = 'BOTH_HIGH'
                    ) AS both_high_count

                FROM projects
                {where_sql}
                """,
                params,
            )

            totals = cur.fetchone()

            # State-level aggregates.
            cur.execute(
                f"""
                SELECT
                    COALESCE(
                        NULLIF(state_name, ''),
                        'Unknown'
                    ) AS state_name,
                    COUNT(*) AS project_count,
                    COALESCE(SUM(overall_score), 0) AS risk_total
                FROM projects
                {where_sql}
                GROUP BY
                    COALESCE(NULLIF(state_name, ''), 'Unknown')
                ORDER BY state_name
                """,
                params,
            )

            state_rows = cur.fetchall()

    state_aggregates = [
        {
            "state": row["state_name"],
            "projectCount": row["project_count"],
            "averageRisk": round(
                float(row["risk_total"]) / row["project_count"],
                2,
            ),
        }
        for row in state_rows
        if row["project_count"]
    ]

    return ProjectAggregatesResponse(
        totalProjects=totals["total_projects"],
        totalSanctionAmount=round(
            float(totals["total_sanction_amount"]),
            2,
        ),
        totalExpenditure=round(
            float(totals["total_expenditure"]),
            2,
        ),
        riskLevelCounts={
            "low": totals["low_count"],
            "moderate": totals["moderate_count"],
            "high": totals["high_count"],
            "critical": totals["critical_count"],
        },
        requiresReviewCount=totals["requires_review_count"],
        stateAggregates=state_aggregates,
        flaggedComponentCounts={
            "cost": totals["cost_flagged"],
            "delay": totals["delay_flagged"],
            "expenditure": totals["expenditure_flagged"],
            "duplicate": totals["duplicate_flagged"],
        },
        mlEligibleCount=totals["ml_eligible_count"],
        mlAnomalyCount=totals["ml_anomaly_count"],
        mlNotApplicableCount=totals["ml_not_applicable_count"],
        mlOnlyCount=totals["ml_only_count"],
        bothHighCount=totals["both_high_count"],
    )
@lru_cache(maxsize=1)
def get_project_filter_options() -> ProjectFilterOptions:
    """Returns cached distinct filter values from PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT state_name
                FROM projects
                WHERE state_name IS NOT NULL
                  AND state_name <> ''
                ORDER BY state_name
                """
            )
            states = [row["state_name"] for row in cur.fetchall()]

            cur.execute(
                """
                SELECT DISTINCT work_category
                FROM projects
                WHERE work_category IS NOT NULL
                  AND work_category <> ''
                ORDER BY work_category
                """
            )
            categories = [row["work_category"] for row in cur.fetchall()]

    return ProjectFilterOptions(
        states=states,
        categories=categories,
        riskLevels=["CRITICAL", "HIGH", "MODERATE", "LOW"],
    )


def get_project_by_id(project_id: str) -> Optional[ProjectRecord]:
    """Returns a single project by ID using PostgreSQL."""

    try:
        numeric_project_id = int(project_id)
    except (TypeError, ValueError):
        return None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM projects
                WHERE project_id = %s
                """,
                (numeric_project_id,),
            )
            db_row = cur.fetchone()

    if db_row is None:
        return None

    record = dict(db_row)

    details = record.pop("details") or {}
    record.update(details)

    # Preserve the existing JSON-backed API contract.
    for field_name in (
        "recommendation_date",
        "sanction_date",
        "first_expenditure_date",
        "last_expenditure_date",
    ):
        value = record.get(field_name)
        if value is not None and hasattr(value, "isoformat"):
            record[field_name] = value.isoformat()

    return _to_project_record(record)


def get_project_official_work_ids(project_id: str) -> Optional[List[int]]:
    """Returns numeric completed-work WORK_ID values for official evidence."""

    try:
        numeric_project_id = int(project_id)
    except (TypeError, ValueError):
        return None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT details->'official_work_ids' AS official_work_ids
                FROM projects
                WHERE project_id = %s
                """,
                (numeric_project_id,),
            )

            row = cur.fetchone()

    if row is None:
        return None

    work_ids = row["official_work_ids"] or []

    return [
        int(work_id)
        for work_id in work_ids
        if isinstance(work_id, int) and not isinstance(work_id, bool)
    ]

def get_alerts(page: int = 1, page_size: int = 50) -> AlertsResponse:
    """Returns a page of projects with detector-provided risk flags from PostgreSQL."""

    offset = (page - 1) * page_size

    flagged_condition = """
        COALESCE((details->'cost'->>'flagged')::boolean, FALSE)
        OR COALESCE((details->'delay'->>'flagged')::boolean, FALSE)
        OR COALESCE((details->'expenditure'->>'flagged')::boolean, FALSE)
        OR COALESCE((details->'duplicate'->>'flagged')::boolean, FALSE)
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM projects
                WHERE {flagged_condition}
                """
            )

            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT
                    project_id,
                    work_description,
                    activity_name,
                    state_name,
                    constituency,
                    mp_name,
                    risk_level,
                    overall_score,

                    COALESCE(
                        (details->'cost'->>'flagged')::boolean,
                        FALSE
                    ) AS cost_flagged,

                    COALESCE(
                        (details->'delay'->>'flagged')::boolean,
                        FALSE
                    ) AS delay_flagged,

                    COALESCE(
                        (details->'expenditure'->>'flagged')::boolean,
                        FALSE
                    ) AS expenditure_flagged,

                    COALESCE(
                        (details->'duplicate'->>'flagged')::boolean,
                        FALSE
                    ) AS duplicate_flagged

                FROM projects
                WHERE {flagged_condition}
                ORDER BY project_id
                LIMIT %s OFFSET %s
                """,
                (page_size, offset),
            )

            rows = cur.fetchall()

    alerts = []

    for row in rows:
        flagged_detectors = []

        if row["cost_flagged"]:
            flagged_detectors.append("cost")

        if row["delay_flagged"]:
            flagged_detectors.append("delay")

        if row["expenditure_flagged"]:
            flagged_detectors.append("expenditure")

        if row["duplicate_flagged"]:
            flagged_detectors.append("duplicate")

        alerts.append(
            AlertRecord(
                projectId=str(row["project_id"]),
                workName=(
                    row["work_description"]
                    or row["activity_name"]
                    or ""
                ),
                state=row["state_name"],
                constituency=row["constituency"],
                mpName=row["mp_name"],
                riskLevel=row["risk_level"],
                overallScore=row["overall_score"],
                flaggedDetectors=flagged_detectors,
            )
        )

    return AlertsResponse(
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=_page_count(total, page_size),
        alerts=alerts,
    )

@lru_cache(maxsize=1)
def get_statistics() -> StatisticsResponse:
    """Returns cached counts from the frozen overall risk labels."""
    aggregates = get_project_aggregates()

    return StatisticsResponse(
        totalProjects=aggregates.totalProjects,
        highRisk=aggregates.riskLevelCounts.high,
        mediumRisk=aggregates.riskLevelCounts.moderate,
        lowRisk=aggregates.riskLevelCounts.low,
        criticalRisk=aggregates.riskLevelCounts.critical,
    )
