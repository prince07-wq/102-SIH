"""
scripts/validate_data.py

Profiles and validates the raw MPLADS datasets (sanctioned.json,
expenditure.json) without modifying them. Writes a machine-readable
report to data/processed/data_profile.json and prints a summary.
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime

SANCTIONED_PATH = os.path.join("data", "raw", "sanctioned.json")
EXPENDITURE_PATH = os.path.join("data", "raw", "expenditure.json")
REPORT_PATH = os.path.join("data", "processed", "data_profile.json")

JOIN_KEY = "WORK_RECOMMENDATION_DTL_ID"

# Formats attempted when parsing date fields. Actual source format is not
# confirmed, so multiple common formats are tried; unparseable values are
# ignored rather than guessed.
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
    """Treats missing key (None passed in), None, or empty/blank string as missing."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def count_missing_field(rows, field):
    """Counts rows where the given field is missing, null, or blank."""
    return sum(1 for row in rows if is_missing(row.get(field)))


def get_unique_ids(rows, field=JOIN_KEY):
    """Returns the set of non-missing unique values for the given field."""
    return {row.get(field) for row in rows if not is_missing(row.get(field))}


def count_duplicate_ids(rows, field=JOIN_KEY):
    """Returns the number of distinct id values that appear more than once."""
    values = [row.get(field) for row in rows if not is_missing(row.get(field))]
    counts = Counter(values)
    return sum(1 for _, c in counts.items() if c > 1)


def distribution_by_field(rows, field):
    """Returns a dict of value -> row count for the given field."""
    counts = Counter()
    for row in rows:
        value = row.get(field)
        key = "MISSING" if is_missing(value) else str(value)
        counts[key] += 1
    return dict(counts)


def safe_parse_date(value):
    """Attempts to parse a date string using known formats. Returns None on failure."""
    if is_missing(value):
        return None
    if not isinstance(value, str):
        return None

    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def date_range(rows, field):
    """Returns (earliest, latest) ISO date strings for a field, ignoring invalid/missing dates."""
    parsed_dates = [safe_parse_date(row.get(field)) for row in rows]
    parsed_dates = [d for d in parsed_dates if d is not None]

    if not parsed_dates:
        return {"earliest": None, "latest": None, "valid_date_count": 0}

    return {
        "earliest": min(parsed_dates).date().isoformat(),
        "latest": max(parsed_dates).date().isoformat(),
        "valid_date_count": len(parsed_dates),
    }


def build_join_validation(sanctioned, expenditure):
    """Computes join validation metrics between sanctioned and expenditure IDs."""
    sanctioned_ids = get_unique_ids(sanctioned)
    expenditure_ids = get_unique_ids(expenditure)

    expenditure_found_in_sanctioned = expenditure_ids & sanctioned_ids
    expenditure_not_found_in_sanctioned = expenditure_ids - sanctioned_ids

    sanctioned_with_expenditure = sanctioned_ids & expenditure_ids
    sanctioned_without_expenditure = sanctioned_ids - expenditure_ids

    total_sanctioned = len(sanctioned_ids)
    pct_with_expenditure = (
        (len(sanctioned_with_expenditure) / total_sanctioned * 100)
        if total_sanctioned > 0
        else 0.0
    )

    return {
        "expenditure_ids_found_in_sanctioned": len(expenditure_found_in_sanctioned),
        "expenditure_ids_not_found_in_sanctioned": len(expenditure_not_found_in_sanctioned),
        "sanctioned_projects_with_expenditure": len(sanctioned_with_expenditure),
        "sanctioned_projects_without_expenditure": len(sanctioned_without_expenditure),
        "percentage_sanctioned_with_expenditure": round(pct_with_expenditure, 2),
    }


def build_expenditure_relationship(expenditure):
    """Computes per-project expenditure record count statistics."""
    ids = [row.get(JOIN_KEY) for row in expenditure if not is_missing(row.get(JOIN_KEY))]
    counts = Counter(ids)

    if not counts:
        return {
            "min_records_per_project": 0,
            "max_records_per_project": 0,
            "average_records_per_project": 0.0,
            "top_20_projects_by_record_count": [],
        }

    values = list(counts.values())
    top_20 = counts.most_common(20)

    return {
        "min_records_per_project": min(values),
        "max_records_per_project": max(values),
        "average_records_per_project": round(sum(values) / len(values), 2),
        "top_20_projects_by_record_count": [
            {"work_recommendation_dtl_id": pid, "record_count": count}
            for pid, count in top_20
        ],
    }


def build_sanctioned_quality(sanctioned):
    return {
        "missing_work_recommendation_dtl_id": count_missing_field(sanctioned, JOIN_KEY),
        "duplicate_work_recommendation_dtl_id": count_duplicate_ids(sanctioned, JOIN_KEY),
        "missing_state_name": count_missing_field(sanctioned, "STATE_NAME"),
        "missing_work_description": count_missing_field(sanctioned, "WORK_DESCRIPTION"),
        "missing_sanction_amount": count_missing_field(sanctioned, "SANCTION_AMOUNT"),
        "missing_sanction_date": count_missing_field(sanctioned, "SANCTION_DATE"),
        "missing_work_stage": count_missing_field(sanctioned, "WORK_STAGE"),
        "missing_ida_name": count_missing_field(sanctioned, "IDA_NAME"),
    }


def build_expenditure_quality(expenditure):
    return {
        "missing_work_recommendation_dtl_id": count_missing_field(expenditure, JOIN_KEY),
        "missing_state_name": count_missing_field(expenditure, "STATE_NAME"),
        "missing_vendor_name": count_missing_field(expenditure, "VENDOR_NAME"),
        "missing_vendor_id": count_missing_field(expenditure, "VENDOR_ID"),
        "missing_expenditure_date": count_missing_field(expenditure, "EXPENDITURE_DATE"),
        "missing_fund_disbursed_amt": count_missing_field(expenditure, "FUND_DISBURSED_AMT"),
        "missing_work_status": count_missing_field(expenditure, "WORK_STATUS"),
        "missing_work_id": count_missing_field(expenditure, "WORK_ID"),
    }


def build_report(sanctioned, expenditure):
    report = {
        "general": {
            "total_sanctioned_rows": len(sanctioned),
            "total_expenditure_rows": len(expenditure),
            "unique_sanctioned_project_ids": len(get_unique_ids(sanctioned)),
            "unique_expenditure_project_ids": len(get_unique_ids(expenditure)),
        },
        "join_validation": build_join_validation(sanctioned, expenditure),
        "sanctioned_data_quality": build_sanctioned_quality(sanctioned),
        "expenditure_data_quality": build_expenditure_quality(expenditure),
        "distributions": {
            "sanctioned_by_state_name": distribution_by_field(sanctioned, "STATE_NAME"),
            "sanctioned_by_work_stage": distribution_by_field(sanctioned, "WORK_STAGE"),
            "expenditure_by_work_status": distribution_by_field(expenditure, "WORK_STATUS"),
            "expenditure_by_state_name": distribution_by_field(expenditure, "STATE_NAME"),
        },
        "expenditure_relationship": build_expenditure_relationship(expenditure),
        "dates": {
            "sanction_date_range": date_range(sanctioned, "SANCTION_DATE"),
            "expenditure_date_range": date_range(expenditure, "EXPENDITURE_DATE"),
        },
    }
    return report


def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(report):
    g = report["general"]
    j = report["join_validation"]
    sq = report["sanctioned_data_quality"]
    eq = report["expenditure_data_quality"]
    er = report["expenditure_relationship"]
    d = report["dates"]

    print("\n--- Data Profile Summary ---")
    print(f"Sanctioned rows: {g['total_sanctioned_rows']} | Unique IDs: {g['unique_sanctioned_project_ids']}")
    print(f"Expenditure rows: {g['total_expenditure_rows']} | Unique IDs: {g['unique_expenditure_project_ids']}")

    print("\nJoin validation:")
    print(f"  Expenditure IDs found in sanctioned: {j['expenditure_ids_found_in_sanctioned']}")
    print(f"  Expenditure IDs NOT found in sanctioned: {j['expenditure_ids_not_found_in_sanctioned']}")
    print(f"  Sanctioned projects with expenditure: {j['sanctioned_projects_with_expenditure']}")
    print(f"  Sanctioned projects without expenditure: {j['sanctioned_projects_without_expenditure']}")
    print(f"  % sanctioned with expenditure: {j['percentage_sanctioned_with_expenditure']}%")

    print("\nSanctioned data quality (missing counts):")
    for key, value in sq.items():
        print(f"  {key}: {value}")

    print("\nExpenditure data quality (missing counts):")
    for key, value in eq.items():
        print(f"  {key}: {value}")

    print("\nExpenditure records per project:")
    print(f"  min: {er['min_records_per_project']}, max: {er['max_records_per_project']}, avg: {er['average_records_per_project']}")

    print("\nDate ranges:")
    print(f"  Sanction date: {d['sanction_date_range']['earliest']} to {d['sanction_date_range']['latest']} "
          f"({d['sanction_date_range']['valid_date_count']} valid dates)")
    print(f"  Expenditure date: {d['expenditure_date_range']['earliest']} to {d['expenditure_date_range']['latest']} "
          f"({d['expenditure_date_range']['valid_date_count']} valid dates)")

    print(f"\nFull report saved to: {REPORT_PATH}")


def main():
    try:
        sanctioned = load_json_list(SANCTIONED_PATH)
        expenditure = load_json_list(EXPENDITURE_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load raw data: {e}")
        sys.exit(1)

    report = build_report(sanctioned, expenditure)

    try:
        save_json(report, REPORT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save report: {e}")
        sys.exit(1)

    print("SUCCESS: Data profiling complete.")
    print_summary(report)


if __name__ == "__main__":
    main()