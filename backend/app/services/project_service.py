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
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from typing import Iterator, List, Optional

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
    EXACT_PROJECT_ID_SCORE,
    MIN_PARTIAL_TOKEN_LENGTH,
    SEARCH_ALIAS_GROUPS,
    SEARCH_FIELD_WEIGHTS,
)

_SERVICE_DIR = os.path.dirname(__file__)
_DATA_PATH = os.path.abspath(
    os.path.join(
        _SERVICE_DIR,
        "..",
        "..",
        "..",
        "data",
        "processed",
        "api_projects.json",
    )
)

_RISK_COMPONENTS = ["cost", "delay", "expenditure", "duplicate"]


@lru_cache(maxsize=1)
def _load_records():
    """Loads and caches the API-ready dataset once per server process."""
    if not os.path.exists(_DATA_PATH):
        raise FileNotFoundError(f"Required processed dataset not found: {_DATA_PATH}")

    with open(_DATA_PATH, "r", encoding="utf-8") as fh:
        records = json.load(fh)

    if not isinstance(records, list):
        raise ValueError(
            f"Expected a JSON list in {_DATA_PATH}, got {type(records).__name__}"
        )

    return records


@lru_cache(maxsize=1)
def _get_project_index():
    """Builds a cached string project-ID lookup for detail requests."""
    index = {}

    for position, record in enumerate(_load_records(), start=1):
        if not isinstance(record, dict):
            raise ValueError(f"Project record {position} must be a JSON object")

        project_id = record.get("project_id")
        if project_id is None or str(project_id).strip() == "":
            raise ValueError(f"Project record {position} has no project_id")

        project_id_text = str(project_id)
        if project_id_text in index:
            raise ValueError(f"Duplicate project_id in API dataset: {project_id_text}")
        index[project_id_text] = record

    return index


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


def _searchable_fields(record):
    """Returns normalized investigation fields and their tokens."""
    vendor_names = " ".join(
        str(vendor.get("vendor_name", ""))
        for vendor in record.get("vendors", [])
        if isinstance(vendor, dict)
    )
    work_ids = " ".join(str(work_id) for work_id in record.get("work_ids", []))
    values = {
        "project_id": record.get("project_id"),
        "activity_name": record.get("activity_name"),
        "work_description": record.get("work_description"),
        "state_name": record.get("state_name"),
        "constituency": record.get("constituency"),
        "mp_name": record.get("mp_name"),
        "ida_name": record.get("ida_name"),
        "work_ids": work_ids,
        "vendor_names": vendor_names,
    }
    document = {}
    all_tokens = []
    for field_name, value in values.items():
        text = _normalize_search_text(value)
        tokens = tuple(text.split())
        document[field_name] = {"text": text, "tokens": tokens}
        all_tokens.extend(tokens)
    document["_all_tokens"] = tuple(all_tokens)
    return document


@lru_cache(maxsize=1)
def _get_search_documents():
    """Builds normalized search documents once, aligned with dataset order."""
    return tuple(_searchable_fields(record) for record in _load_records())


@lru_cache(maxsize=1)
def _get_search_token_index():
    """Maps normalized field tokens to dataset positions for fast candidates."""
    token_positions = defaultdict(set)
    for position, document in enumerate(_get_search_documents()):
        for token in set(document["_all_tokens"]):
            token_positions[token].add(position)
    return {
        token: frozenset(positions) for token, positions in token_positions.items()
    }


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


def _group_matches(tokens, group):
    """Checks whether any alternate wording for a query concept matches."""
    return any(_variant_matches(tokens, variant) for variant in group)


@lru_cache(maxsize=256)
def _positions_for_token(query_token):
    """Returns all records containing an exact or partial token match."""
    positions = set()
    for document_token, token_positions in _get_search_token_index().items():
        if _token_matches(query_token, document_token):
            positions.update(token_positions)
    return frozenset(positions)


def _candidate_positions(groups):
    """Uses the token index to AND query concepts and OR alias variants."""
    candidates = None
    for group in groups:
        group_positions = set()
        for variant in group:
            variant_positions = None
            for token in variant:
                token_positions = _positions_for_token(token)
                variant_positions = (
                    set(token_positions)
                    if variant_positions is None
                    else variant_positions.intersection(token_positions)
                )
                if not variant_positions:
                    break
            if variant_positions:
                group_positions.update(variant_positions)
        candidates = (
            group_positions
            if candidates is None
            else candidates.intersection(group_positions)
        )
        if not candidates:
            return ()
    return tuple(candidates or ())


def _search_score(document, search_value, groups):
    """Returns a relevance score, or None when the project does not match."""
    project_id = document["project_id"]["text"]
    if search_value == project_id:
        return EXACT_PROJECT_ID_SCORE

    all_tokens = document["_all_tokens"]
    if not groups or not all(_group_matches(all_tokens, group) for group in groups):
        return None

    score = 0
    for field_name, weight in SEARCH_FIELD_WEIGHTS.items():
        field = document[field_name]
        matching_groups = sum(
            _group_matches(field["tokens"], group) for group in groups
        )
        score += matching_groups * weight
        if matching_groups == len(groups):
            score += weight * 2
        if search_value == field["text"]:
            score += weight * 4
        elif search_value and search_value in field["text"]:
            score += weight * 2

    if project_id and search_value in project_id:
        score += SEARCH_FIELD_WEIGHTS["project_id"] * 2
    return score


@lru_cache(maxsize=16)
def _ranked_search_positions(search_value):
    """Caches relevance-ranked dataset positions for recent search phrases."""
    documents = _get_search_documents()
    exact_id_positions = tuple(
        position
        for position, document in enumerate(documents)
        if document["project_id"]["text"] == search_value
    )
    if exact_id_positions:
        return exact_id_positions

    groups = _query_groups(search_value)
    ranked_matches = []
    for position in _candidate_positions(groups):
        document = documents[position]
        score = _search_score(document, search_value, groups)
        if score is not None:
            ranked_matches.append((score, position))
    ranked_matches.sort(key=lambda item: (-item[0], item[1]))
    return tuple(position for _, position in ranked_matches)


def _normalize_filters(risk, state, category, search):
    """Normalizes public filter values for consistent list and aggregate matching."""
    return {
        "risk": _risk_filter_value(risk),
        "state": state.strip().casefold() if state else None,
        "category": category.strip().casefold() if category else None,
        "search": _normalize_search_text(search) if search else None,
    }


def _record_matches_filters(record, filters):
    """Applies non-search filters to one project record."""
    if filters["risk"] and str(record.get("risk_level", "")).upper() != filters["risk"]:
        return False
    if filters["state"] and filters["state"] not in str(record.get("state_name", "")).casefold():
        return False
    if filters["category"] and str(record.get("work_category", "")).casefold() != filters["category"]:
        return False
    return True


def _matching_records(risk=None, state=None, category=None, search=None):
    """Returns all matches, relevance-ranked before any pagination."""
    filters = _normalize_filters(risk, state, category, search)
    records = _load_records()
    if not filters["search"]:
        return (
            record for record in records if _record_matches_filters(record, filters)
        )

    return (
        records[position]
        for position in _ranked_search_positions(filters["search"])
        if _record_matches_filters(records[position], filters)
    )


def get_all_projects(
    risk: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> ProjectListResponse:
    """Returns one filtered page without materializing every API model."""
    start = (page - 1) * page_size
    end = start + page_size
    total = 0
    page_records = []

    for record in _matching_records(risk, state, category, search):
        if start <= total < end:
            page_records.append(_to_project_record(record))
        total += 1

    return ProjectListResponse(
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=_page_count(total, page_size),
        projects=page_records,
    )


def iter_project_export(
    risk: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> Iterator[str]:
    """Streams a filtered CSV export without building API models in memory."""
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
    writer = csv.DictWriter(buffer, fieldnames=field_names, lineterminator="\n")
    writer.writeheader()
    yield buffer.getvalue()

    for record in _matching_records(risk, state, category, search):
        buffer.seek(0)
        buffer.truncate(0)
        writer.writerow(
            {
                "project_id": record.get("project_id"),
                "work_name": record.get("work_description")
                or record.get("activity_name"),
                "state": record.get("state_name"),
                "constituency": record.get("constituency"),
                "mp_name": record.get("mp_name"),
                "authority": record.get("ida_name"),
                "category": record.get("work_category"),
                "sanction_amount": record.get("sanction_amount"),
                "total_expenditure": record.get("total_disbursed"),
                "risk_level": record.get("risk_level"),
                "overall_score": record.get("overall_score"),
                "flag_count": record.get("flag_count"),
                **{
                    f"{component_name}_flagged": record.get(
                        component_name, {}
                    ).get("flagged", False)
                    for component_name in _RISK_COMPONENTS
                },
            }
        )
        yield buffer.getvalue()


@lru_cache(maxsize=128)
def get_project_aggregates(
    risk: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> ProjectAggregatesResponse:
    """Aggregates the complete filtered result set before table pagination."""
    total_projects = 0
    total_sanction_amount = 0.0
    total_expenditure = 0.0
    requires_review_count = 0
    risk_level_counts = Counter()
    flagged_component_counts = Counter()
    state_totals = defaultdict(lambda: {"project_count": 0, "risk_total": 0.0})

    for record in _matching_records(risk, state, category, search):
        total_projects += 1
        total_sanction_amount += float(record.get("sanction_amount") or 0)
        total_expenditure += float(record.get("total_disbursed") or 0)
        risk_level_counts[str(record.get("risk_level", "")).upper()] += 1

        flagged_components = [
            component_name
            for component_name in _RISK_COMPONENTS
            if record.get(component_name, {}).get("flagged") is True
        ]
        if flagged_components:
            requires_review_count += 1
        for component_name in flagged_components:
            flagged_component_counts[component_name] += 1

        state_name = str(record.get("state_name") or "Unknown")
        state_totals[state_name]["project_count"] += 1
        state_totals[state_name]["risk_total"] += float(record.get("overall_score") or 0)

    state_aggregates = [
        {
            "state": state_name,
            "projectCount": values["project_count"],
            "averageRisk": round(values["risk_total"] / values["project_count"], 2),
        }
        for state_name, values in sorted(state_totals.items())
    ]

    return ProjectAggregatesResponse(
        totalProjects=total_projects,
        totalSanctionAmount=round(total_sanction_amount, 2),
        totalExpenditure=round(total_expenditure, 2),
        riskLevelCounts={
            "low": risk_level_counts.get("LOW", 0),
            "moderate": risk_level_counts.get("MODERATE", 0),
            "high": risk_level_counts.get("HIGH", 0),
            "critical": risk_level_counts.get("CRITICAL", 0),
        },
        requiresReviewCount=requires_review_count,
        stateAggregates=state_aggregates,
        flaggedComponentCounts={
            component_name: flagged_component_counts.get(component_name, 0)
            for component_name in _RISK_COMPONENTS
        },
    )


@lru_cache(maxsize=1)
def get_project_filter_options() -> ProjectFilterOptions:
    """Returns cached distinct filter values from the processed dataset."""
    records = _load_records()
    states = sorted(
        {str(record.get("state_name")) for record in records if record.get("state_name")}
    )
    categories = sorted(
        {
            str(record.get("work_category"))
            for record in records
            if record.get("work_category")
        }
    )
    return ProjectFilterOptions(
        states=states,
        categories=categories,
        riskLevels=["CRITICAL", "HIGH", "MODERATE", "LOW"],
    )


def get_project_by_id(project_id: str) -> Optional[ProjectRecord]:
    """Returns a single project by ID using the cached lookup."""
    record = _get_project_index().get(str(project_id))
    return _to_project_record(record) if record is not None else None


def get_alerts(page: int = 1, page_size: int = 50) -> AlertsResponse:
    """Returns a page of projects with detector-provided risk flags."""
    start = (page - 1) * page_size
    end = start + page_size
    total = 0
    alerts: List[AlertRecord] = []

    for record in _load_records():
        flagged_detectors = [
            component_name
            for component_name in _RISK_COMPONENTS
            if record.get(component_name, {}).get("flagged") is True
        ]
        if not flagged_detectors:
            continue

        if start <= total < end:
            alerts.append(
                AlertRecord(
                    projectId=str(record.get("project_id")),
                    workName=record.get("work_description")
                    or record.get("activity_name")
                    or "",
                    state=record.get("state_name"),
                    constituency=record.get("constituency"),
                    mpName=record.get("mp_name"),
                    riskLevel=record.get("risk_level"),
                    overallScore=record.get("overall_score"),
                    flaggedDetectors=flagged_detectors,
                )
            )
        total += 1

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
