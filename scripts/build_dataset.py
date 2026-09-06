"""
scripts/build_dataset.py

Builds a clean one-record-per-project dataset by joining sanctioned
project data with aggregated expenditure data, using
WORK_RECOMMENDATION_DTL_ID as the join key.

Input:
  data/raw/sanctioned.json
  data/raw/expenditure.json
  data/raw/works_completed.json

Output:
  data/processed/projects.json
"""

import json
import os
import sys
from datetime import datetime

SANCTIONED_PATH = os.path.join("data", "raw", "sanctioned.json")
EXPENDITURE_PATH = os.path.join("data", "raw", "expenditure.json")
WORKS_COMPLETED_PATH = os.path.join("data", "raw", "works_completed.json")
OUTPUT_PATH = os.path.join("data", "processed", "projects.json")

JOIN_KEY = "WORK_RECOMMENDATION_DTL_ID"

# Sanctioned fields to preserve, mapped to output field names.
SANCTIONED_FIELD_MAP = {
    "ACTIVITY_NAME": "activity_name",
    "WORK_CATEGORY": "work_category",
    "WORK_DESCRIPTION": "work_description",
    "STATE_NAME": "state_name",
    "CONSTITUENCY": "constituency",
    "MP_NAME": "mp_name",
    "IDA_NAME": "ida_name",
    "RECOMMENDATION_DATE": "recommendation_date",
    "SANCTION_DATE": "sanction_date",
    "SANCTION_AMOUNT": "sanction_amount",
    "WORK_STAGE": "work_stage",
    "TENURE": "tenure",
    "HOUSE_OF_PARLIAMENT": "house_of_parliament",
}

# Sanctioned fields whose values are dates and must be ISO-normalized.
SANCTIONED_DATE_FIELDS = {"RECOMMENDATION_DATE", "SANCTION_DATE"}

# Date formats attempted when parsing. Actual source format is not
# confirmed, so several common formats are tried; unparseable values
# become null rather than being guessed.
DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d-%b-%Y",
    "%d %b %Y",
]


def load_json_list(filepath):
    """Loads a JSON file and validates that its top-level structure is a list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {filepath}, got {type(data).__name__}")

    return data


def is_missing(value):
    """Treats None or blank/whitespace-only string as missing."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def safe_parse_date(value):
    """Attempts to parse a date string using known formats. Returns a datetime or None."""
    if is_missing(value) or not isinstance(value, str):
        return None

    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def to_iso_date(value):
    """Converts a raw date value to an ISO 'YYYY-MM-DD' string, or None if invalid/missing."""
    parsed = safe_parse_date(value)
    return parsed.date().isoformat() if parsed else None


def safe_parse_amount(value):
    """
    Safely parses a monetary value that may be a number or a string.

    Returns (amount, is_malformed):
      - missing/null value -> (0.0, False)  [nothing to add, not an error]
      - valid number/numeric string -> (float(value), False)
      - non-empty but unparseable -> (0.0, True)  [malformed, tracked]
    """
    if is_missing(value):
        return 0.0, False

    if isinstance(value, (int, float)):
        return float(value), False

    if isinstance(value, str):
        text = value.strip().replace(",", "")
        try:
            return float(text), False
        except ValueError:
            return 0.0, True

    # Any other unexpected type is treated as malformed.
    return 0.0, True


def build_sanctioned_lookup(sanctioned_rows):
    """
    Builds project_id -> sanctioned record dict for rows with a valid
    WORK_RECOMMENDATION_DTL_ID. Returns (lookup, valid_count).
    """
    lookup = {}
    for row in sanctioned_rows:
        project_id = row.get(JOIN_KEY)
        if is_missing(project_id):
            continue
        lookup[project_id] = row
    return lookup, len(lookup)


def init_project_record(project_id, sanctioned_row):
    """Creates the base output record for a project from its sanctioned row."""
    record = {"project_id": project_id}

    for source_field, output_field in SANCTIONED_FIELD_MAP.items():
        raw_value = sanctioned_row.get(source_field)
        if source_field in SANCTIONED_DATE_FIELDS:
            record[output_field] = to_iso_date(raw_value)
        else:
            record[output_field] = raw_value

    # Expenditure aggregates, defaulted for projects with no expenditure.
    record["has_expenditure"] = False
    record["expenditure_record_count"] = 0
    record["total_disbursed"] = 0
    record["unique_vendor_count"] = 0
    record["first_expenditure_date"] = None
    record["last_expenditure_date"] = None
    record["vendors"] = []
    record["work_ids"] = []
    record["official_work_ids"] = []
    record["has_official_attachment"] = False

    return record


def aggregate_expenditure(expenditure_rows, sanctioned_lookup, stats):
    """
    Groups expenditure rows by project_id and computes per-project
    aggregates. Updates `stats` in place. Returns a dict:
    project_id -> aggregate dict.
    """
    aggregates = {}

    for row in expenditure_rows:
        project_id = row.get(JOIN_KEY)

        if is_missing(project_id):
            stats["expenditure_skipped_missing_id"] += 1
            continue

        stats["expenditure_rows_processed"] += 1

        if project_id not in sanctioned_lookup:
            stats["expenditure_ids_not_in_sanctioned"] += 1
            continue

        agg = aggregates.setdefault(project_id, {
            "record_count": 0,
            "total_disbursed": 0.0,
            "vendors": {},  # vendor_id -> vendor_name (dedup by id)
            "dates": [],
            "work_ids": set(),
        })

        agg["record_count"] += 1

        amount, malformed = safe_parse_amount(row.get("FUND_DISBURSED_AMT"))
        if malformed:
            stats["malformed_fund_disbursed_amt"] += 1
        agg["total_disbursed"] += amount

        vendor_id = row.get("VENDOR_ID")
        vendor_name = row.get("VENDOR_NAME")
        if not is_missing(vendor_id) or not is_missing(vendor_name):
            # Use vendor_id as dedup key when present, else fall back to name.
            key = vendor_id if not is_missing(vendor_id) else f"__name__:{vendor_name}"
            if key not in agg["vendors"]:
                agg["vendors"][key] = {
                    "vendor_id": vendor_id if not is_missing(vendor_id) else None,
                    "vendor_name": vendor_name if not is_missing(vendor_name) else None,
                }

        parsed_date = safe_parse_date(row.get("EXPENDITURE_DATE"))
        if parsed_date:
            agg["dates"].append(parsed_date)

        work_id = row.get("WORK_ID")
        if not is_missing(work_id):
            agg["work_ids"].add(work_id)

    return aggregates


def apply_expenditure_aggregates(record, agg, stats):
    """Merges a computed expenditure aggregate into a project's output record."""
    record["has_expenditure"] = True
    record["expenditure_record_count"] = agg["record_count"]
    record["total_disbursed"] = round(agg["total_disbursed"], 2)
    record["vendors"] = list(agg["vendors"].values())
    record["unique_vendor_count"] = len(agg["vendors"])

    if agg["dates"]:
        record["first_expenditure_date"] = min(agg["dates"]).date().isoformat()
        record["last_expenditure_date"] = max(agg["dates"]).date().isoformat()

    work_ids_sorted = sorted(agg["work_ids"], key=lambda x: str(x))
    record["work_ids"] = work_ids_sorted
    if len(work_ids_sorted) > 1:
        stats["projects_with_multiple_work_ids"] += 1


def parse_official_work_id(value):
    """Returns a numeric completed-work WORK_ID, or None when malformed."""
    if isinstance(value, bool) or is_missing(value):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def has_completed_attachment(row):
    """Conservatively recognizes completed-work attachment availability."""
    return row.get("FILE_STATUS") is True and not is_missing(row.get("ATTACH_ID"))


def aggregate_completed_works(completed_rows, sanctioned_lookup, stats):
    """Groups numeric official WORK_ID values and attachment availability by project."""
    aggregates = {}

    for position, row in enumerate(completed_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Completed-work record {position} must be an object")

        project_id = row.get(JOIN_KEY)
        if is_missing(project_id):
            stats["completed_rows_skipped_missing_id"] += 1
            continue
        stats["completed_rows_processed"] += 1

        if project_id not in sanctioned_lookup:
            stats["completed_ids_not_in_sanctioned"] += 1
            continue

        aggregate = aggregates.setdefault(project_id, {
            "official_work_ids": set(),
            "has_official_attachment": False,
        })
        official_work_id = parse_official_work_id(row.get("WORK_ID"))
        if official_work_id is None:
            stats["completed_rows_malformed_work_id"] += 1
        else:
            aggregate["official_work_ids"].add(official_work_id)

        if has_completed_attachment(row):
            aggregate["has_official_attachment"] = True

    return aggregates


def apply_completed_work_aggregates(record, aggregate, stats):
    """Adds official completed-work identifiers without changing textual work_ids."""
    official_work_ids = sorted(aggregate["official_work_ids"])
    record["official_work_ids"] = official_work_ids
    record["has_official_attachment"] = aggregate["has_official_attachment"]
    if len(official_work_ids) > 1:
        stats["projects_with_multiple_official_work_ids"] += 1
    if record["has_official_attachment"]:
        stats["projects_with_official_attachment"] += 1


def build_projects(
    sanctioned_lookup,
    expenditure_aggregates,
    completed_work_aggregates,
    stats,
):
    """Builds the final list of project records."""
    projects = []

    for project_id, sanctioned_row in sanctioned_lookup.items():
        record = init_project_record(project_id, sanctioned_row)

        agg = expenditure_aggregates.get(project_id)
        if agg:
            apply_expenditure_aggregates(record, agg, stats)
            stats["projects_with_expenditure"] += 1
        else:
            stats["projects_without_expenditure"] += 1

        completed_aggregate = completed_work_aggregates.get(project_id)
        if completed_aggregate:
            apply_completed_work_aggregates(record, completed_aggregate, stats)

        projects.append(record)

    return projects


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_sanity_checks(stats, projects_written):
    """Prints warnings if key metrics deviate noticeably from expected ballpark figures."""
    expectations = {
        "projects written": (projects_written, 78079),
        "projects with expenditure": (stats["projects_with_expenditure"], 55656),
        "projects without expenditure": (stats["projects_without_expenditure"], 22423),
    }

    print("\n--- Sanity Checks (approximate expectations) ---")
    for label, (actual, expected) in expectations.items():
        diff = abs(actual - expected)
        flag = "OK" if diff <= max(50, expected * 0.02) else "CHECK THIS"
        print(f"  {label}: {actual} (expected ~{expected}) [{flag}]")


def print_summary(stats, projects_written, output_path):
    print("\n--- Build Summary ---")
    print(f"Valid sanctioned projects processed: {stats['valid_sanctioned_projects']}")
    print(f"Projects written: {projects_written}")
    print(f"Projects with expenditure: {stats['projects_with_expenditure']}")
    print(f"Projects without expenditure: {stats['projects_without_expenditure']}")
    print(f"Expenditure rows processed: {stats['expenditure_rows_processed']}")
    print(f"Expenditure rows skipped (missing project ID): {stats['expenditure_skipped_missing_id']}")
    print(f"Expenditure IDs not matching sanctioned projects: {stats['expenditure_ids_not_in_sanctioned']}")
    print(f"Malformed FUND_DISBURSED_AMT values: {stats['malformed_fund_disbursed_amt']}")
    print(f"Projects with multiple distinct WORK_ID values: {stats['projects_with_multiple_work_ids']}")
    print(f"Completed-work rows processed: {stats['completed_rows_processed']}")
    print(f"Completed-work rows skipped (missing project ID): {stats['completed_rows_skipped_missing_id']}")
    print(f"Completed-work IDs not matching sanctioned projects: {stats['completed_ids_not_in_sanctioned']}")
    print(f"Completed-work rows with malformed WORK_ID: {stats['completed_rows_malformed_work_id']}")
    print(f"Projects with multiple official WORK_ID values: {stats['projects_with_multiple_official_work_ids']}")
    print(f"Projects with official attachment metadata: {stats['projects_with_official_attachment']}")
    print(f"Output path: {output_path}")


def init_stats():
    """Creates counters used while joining raw project datasets."""
    return {
        "valid_sanctioned_projects": 0,
        "expenditure_rows_processed": 0,
        "expenditure_skipped_missing_id": 0,
        "expenditure_ids_not_in_sanctioned": 0,
        "malformed_fund_disbursed_amt": 0,
        "projects_with_expenditure": 0,
        "projects_without_expenditure": 0,
        "projects_with_multiple_work_ids": 0,
        "completed_rows_processed": 0,
        "completed_rows_skipped_missing_id": 0,
        "completed_ids_not_in_sanctioned": 0,
        "completed_rows_malformed_work_id": 0,
        "projects_with_multiple_official_work_ids": 0,
        "projects_with_official_attachment": 0,
    }


def main():
    try:
        sanctioned_rows = load_json_list(SANCTIONED_PATH)
        expenditure_rows = load_json_list(EXPENDITURE_PATH)
        completed_rows = load_json_list(WORKS_COMPLETED_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load raw data: {e}")
        sys.exit(1)

    stats = init_stats()

    sanctioned_lookup, valid_count = build_sanctioned_lookup(sanctioned_rows)
    stats["valid_sanctioned_projects"] = valid_count

    expenditure_aggregates = aggregate_expenditure(expenditure_rows, sanctioned_lookup, stats)
    completed_work_aggregates = aggregate_completed_works(
        completed_rows, sanctioned_lookup, stats
    )
    projects = build_projects(
        sanctioned_lookup,
        expenditure_aggregates,
        completed_work_aggregates,
        stats,
    )

    try:
        save_json(projects, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    print("SUCCESS: Dataset build complete.")
    print_summary(stats, len(projects), OUTPUT_PATH)
    run_sanity_checks(stats, len(projects))


if __name__ == "__main__":
    main()
