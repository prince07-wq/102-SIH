import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db import get_connection


DATA_PATH = PROJECT_ROOT / "data" / "processed" / "api_projects.json"

JSONB_FIELDS = (
    "cost",
    "delay",
    "expenditure",
    "duplicate",
    "vendors",
    "work_ids",
    "official_work_ids",
    "similar_projects",
)

COLUMNS = [
    "project_id",
    "activity_name",
    "work_category",
    "work_description",
    "state_name",
    "constituency",
    "mp_name",
    "ida_name",
    "recommendation_date",
    "sanction_date",
    "sanction_amount",
    "work_stage",
    "tenure",
    "house_of_parliament",
    "has_expenditure",
    "expenditure_record_count",
    "total_disbursed",
    "unique_vendor_count",
    "first_expenditure_date",
    "last_expenditure_date",
    "has_official_attachment",
    "overall_score",
    "risk_level",
    "flag_count",
    "base_score",
    "strongest_detector",
    "multi_signal_bonus",
    "score_capped",
    "ml_eligible",
    "ml_status",
    "ml_raw_score",
    "ml_anomaly_value",
    "ml_anomaly_score",
    "ml_is_anomaly",
    "ml_anomaly_level",
    "ml_rule_agreement",
    "ml_project_age_days",
    "ml_days_to_first_expenditure",
    "ml_expenditure_record_count",
    "ml_unique_vendor_count",
    "ml_disbursement_ratio",
    "ml_work_stage",
    "details",
    "vendor_names",
    "work_ids_text",
]


def build_vendor_names(details):
    """Builds searchable vendor text from the preserved vendor details."""
    return " ".join(
        str(vendor["vendor_name"])
        for vendor in details.get("vendors") or []
        if isinstance(vendor, dict) and vendor.get("vendor_name") is not None
    )


def build_work_ids_text(details):
    """Builds searchable work-ID text from the preserved work-ID details."""
    return " ".join(
        str(work_id)
        for work_id in details.get("work_ids") or []
        if work_id is not None
    )


def build_row(project):
    details = {
        key: project.get(key)
        for key in JSONB_FIELDS
    }

    values = []

    for column in COLUMNS:
        if column == "details":
            values.append(json.dumps(details))
        elif column == "vendor_names":
            values.append(build_vendor_names(details))
        elif column == "work_ids_text":
            values.append(build_work_ids_text(details))
        else:
            values.append(project.get(column))

    return values


def main():
    print("Loading dataset...")

    with DATA_PATH.open("r", encoding="utf-8") as f:
        projects = json.load(f)

    print(f"Loaded {len(projects)} projects")

    placeholders = ", ".join(["%s"] * len(COLUMNS))
    column_sql = ", ".join(COLUMNS)
    update_sql = ", ".join(
        f"{column} = EXCLUDED.{column}"
        for column in COLUMNS
        if column != "project_id"
    )

    sql = f"""
        INSERT INTO projects ({column_sql})
        VALUES ({placeholders})
        ON CONFLICT (project_id)
        DO UPDATE SET {update_sql}
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            batch = []

            for i, project in enumerate(projects, start=1):
                batch.append(build_row(project))

                if len(batch) >= 1000:
                    cur.executemany(sql, batch)
                    batch.clear()

                    print(f"Imported {i}/{len(projects)}")

            if batch:
                cur.executemany(sql, batch)

        conn.commit()

    print("Import complete.")


if __name__ == "__main__":
    main()
