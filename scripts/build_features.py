"""
scripts/build_features.py

Builds a feature dataset for later anomaly detection from
data/processed/projects.json. Adds derived numeric/date features and
comparison-group statistics (by normalized activity type, state+normalized activity type,
work_category, and state_name+work_category).

Does NOT calculate risk scores, anomaly scores, or perform any ML.
"""
import re
import json
import os
import sys
import statistics
from collections import defaultdict, Counter
from datetime import date

PROJECTS_PATH = os.path.join("data", "processed", "projects.json")
OUTPUT_PATH = os.path.join("data", "processed", "features.json")

# Fixed analysis date so results are reproducible (per confirmed requirement).
ANALYSIS_DATE = date(2026, 8, 27)

# Fields copied unchanged from each project record into the feature record.
PRESERVED_FIELDS = [
    "project_id",
    "activity_name",
    "normalized_activity_name",
    "work_category",
    "work_description",
    "state_name",
    "constituency",
    "mp_name",
    "ida_name",
    "sanction_date",
    "sanction_amount",
    "work_stage",
    "has_expenditure",
    "expenditure_record_count",
    "total_disbursed",
    "unique_vendor_count",
    "first_expenditure_date",
    "last_expenditure_date",
]

MISSING_GROUP_LABEL = "__MISSING__"



def load_projects(filepath):
    """Loads projects.json and validates that its top-level structure is a list."""
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


def safe_parse_number(value):
    """Safely parses a numeric value that may already be a number or a string. Returns float or None."""
    if is_missing(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            return None
    return None


def safe_parse_iso_date(value):
    """Parses an ISO 'YYYY-MM-DD' string into a date object. Returns None if missing/invalid."""
    if is_missing(value) or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def copy_preserved_fields(project):
    """Copies preserved project fields and adds the normalized activity type."""
    record = {
        field: project.get(field)
        for field in PRESERVED_FIELDS
        if field != "normalized_activity_name"
    }
    record["normalized_activity_name"] = normalize_activity_name(project.get("activity_name"))
    return record


def compute_date_features(project, sanction_amount_numeric):
    """Computes days_since_sanction, disbursement_ratio, days_to_first_expenditure,
    expenditure_span_days, and expenditure_frequency for a single project."""
    features = {}

    sanction_date = safe_parse_iso_date(project.get("sanction_date"))
    first_exp_date = safe_parse_iso_date(project.get("first_expenditure_date"))
    last_exp_date = safe_parse_iso_date(project.get("last_expenditure_date"))

    # days_since_sanction
    features["days_since_sanction"] = (
        (ANALYSIS_DATE - sanction_date).days if sanction_date else None
    )

    # disbursement_ratio
    total_disbursed = project.get("total_disbursed")
    total_disbursed_numeric = safe_parse_number(total_disbursed)
    if sanction_amount_numeric is not None and sanction_amount_numeric > 0 and total_disbursed_numeric is not None:
        features["disbursement_ratio"] = round(total_disbursed_numeric / sanction_amount_numeric, 4)
    else:
        features["disbursement_ratio"] = None

    # days_to_first_expenditure
    if sanction_date and first_exp_date:
        features["days_to_first_expenditure"] = (first_exp_date - sanction_date).days
    else:
        features["days_to_first_expenditure"] = None

    # expenditure_span_days
    if first_exp_date and last_exp_date:
        features["expenditure_span_days"] = (last_exp_date - first_exp_date).days
    else:
        features["expenditure_span_days"] = None

    # expenditure_frequency (only when expenditure exists)
    if project.get("has_expenditure"):
        record_count = project.get("expenditure_record_count") or 0
        span = features["expenditure_span_days"] if features["expenditure_span_days"] is not None else 0
        denominator = max(span, 1)
        features["expenditure_frequency"] = round(record_count / denominator, 4)
    else:
        features["expenditure_frequency"] = None

    return features


def normalize_activity_name(activity_name):
    """
    Removes the unique MPLADS work prefix from ACTIVITY_NAME values so projects
    with the same underlying activity type can be compared together.

    Example:
    WS/MP620/2024-2025/133166-Construction of buildings for community cultural activities
    -> Construction of buildings for community cultural activities
    """
    if is_missing(activity_name) or not isinstance(activity_name, str):
        return None

    text = activity_name.strip()

    # Match the final numeric work identifier followed by the real activity text.
    # The prefix itself may contain hyphens (e.g. 2024-2025), so a simple split("-", 1)
    # would be incorrect.
    match = re.match(r"^WS/.*/\d+-(.+)$", text, flags=re.IGNORECASE)
    if match:
        normalized = match.group(1).strip()
        return normalized if normalized else None

    # Preserve non-standard activity values rather than discarding them.
    return text or None


def get_group_key(project):
    """Returns peer-group keys, using a placeholder for missing values."""
    activity = normalize_activity_name(project.get("activity_name"))
    category = project.get("work_category")
    state = project.get("state_name")

    activity_key = activity if not is_missing(activity) else MISSING_GROUP_LABEL
    category_key = category if not is_missing(category) else MISSING_GROUP_LABEL
    state_key = state if not is_missing(state) else MISSING_GROUP_LABEL

    return (
        activity_key,
        (state_key, activity_key),
        category_key,
        (state_key, category_key),
    )


def calculate_distribution_statistics(amounts_by_group):
    """Calculates Q1, Q3, and IQR for each group using inclusive quartiles."""
    distribution_stats = {}

    for key, values in amounts_by_group.items():
        if not values:
            continue

        if len(values) == 1:
            q1 = values[0]
            q3 = values[0]
        else:
            q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")

        distribution_stats[key] = {
            "q1": q1,
            "q3": q3,
            "iqr": q3 - q1,
        }

    return distribution_stats


def collect_group_statistics(projects, sanction_amounts):
    """
    First pass over projects: collects valid sanction amounts and total
    membership counts per group. Returns:
      activity_medians, state_activity_medians,
      category_medians, state_category_medians,
      activity_sizes, state_activity_sizes,
      category_sizes, state_category_sizes,
      distribution_stats
    """
    activity_amounts = defaultdict(list)
    state_activity_amounts = defaultdict(list)
    category_amounts = defaultdict(list)
    state_category_amounts = defaultdict(list)
    activity_sizes = Counter()
    state_activity_sizes = Counter()
    category_sizes = Counter()
    state_category_sizes = Counter()

    for project, amount in zip(projects, sanction_amounts):
        activity_key, state_activity_key, category_key, state_category_key = \
            get_group_key(project)

        activity_sizes[activity_key] += 1
        state_activity_sizes[state_activity_key] += 1
        category_sizes[category_key] += 1
        state_category_sizes[state_category_key] += 1

        if amount is not None:
            activity_amounts[activity_key].append(amount)
            state_activity_amounts[state_activity_key].append(amount)
            category_amounts[category_key].append(amount)
            state_category_amounts[state_category_key].append(amount)

    activity_medians = {
        key: statistics.median(values) for key, values in activity_amounts.items() if values
    }
    state_activity_medians = {
        key: statistics.median(values) for key, values in state_activity_amounts.items() if values
    }
    category_medians = {
        key: statistics.median(values) for key, values in category_amounts.items() if values
    }
    state_category_medians = {
        key: statistics.median(values) for key, values in state_category_amounts.items() if values
    }
    distribution_stats = {
        "activity": calculate_distribution_statistics(activity_amounts),
        "state_activity": calculate_distribution_statistics(state_activity_amounts),
        "category": calculate_distribution_statistics(category_amounts),
        "state_category": calculate_distribution_statistics(state_category_amounts),
    }

    return (
        activity_medians,
        state_activity_medians,
        category_medians,
        state_category_medians,
        activity_sizes,
        state_activity_sizes,
        category_sizes,
        state_category_sizes,
        distribution_stats,
    )


def compute_group_features(project, amount, activity_medians, state_activity_medians,
                           category_medians, state_category_medians, activity_sizes,
                           state_activity_sizes, category_sizes, state_category_sizes,
                           distribution_stats):
    """Computes group-comparison features for a single project."""
    activity_key, state_activity_key, category_key, state_category_key = \
        get_group_key(project)

    activity_median = activity_medians.get(activity_key)
    state_activity_median = state_activity_medians.get(state_activity_key)
    category_median = category_medians.get(category_key)
    state_category_median = state_category_medians.get(state_category_key)
    activity_distribution = distribution_stats["activity"].get(activity_key, {})
    state_activity_distribution = distribution_stats["state_activity"].get(
        state_activity_key, {}
    )
    category_distribution = distribution_stats["category"].get(category_key, {})
    state_category_distribution = distribution_stats["state_category"].get(
        state_category_key, {}
    )

    features = {
        "activity_median_sanction_amount": activity_median,
        "activity_q1_sanction_amount": activity_distribution.get("q1"),
        "activity_q3_sanction_amount": activity_distribution.get("q3"),
        "activity_iqr_sanction_amount": activity_distribution.get("iqr"),
        "activity_group_size": activity_sizes.get(activity_key, 0),
        "state_activity_median_sanction_amount": state_activity_median,
        "state_activity_q1_sanction_amount": state_activity_distribution.get("q1"),
        "state_activity_q3_sanction_amount": state_activity_distribution.get("q3"),
        "state_activity_iqr_sanction_amount": state_activity_distribution.get("iqr"),
        "state_activity_group_size": state_activity_sizes.get(state_activity_key, 0),
        "category_median_sanction_amount": category_median,
        "category_q1_sanction_amount": category_distribution.get("q1"),
        "category_q3_sanction_amount": category_distribution.get("q3"),
        "category_iqr_sanction_amount": category_distribution.get("iqr"),
        "state_category_median_sanction_amount": state_category_median,
        "state_category_q1_sanction_amount": state_category_distribution.get("q1"),
        "state_category_q3_sanction_amount": state_category_distribution.get("q3"),
        "state_category_iqr_sanction_amount": state_category_distribution.get("iqr"),
        "category_group_size": category_sizes.get(category_key, 0),
        "state_category_group_size": state_category_sizes.get(state_category_key, 0),
    }

    if amount is not None and activity_median is not None and activity_median > 0:
        features["cost_vs_activity_median"] = round(amount / activity_median, 4)
    else:
        features["cost_vs_activity_median"] = None

    if amount is not None and state_activity_median is not None and state_activity_median > 0:
        features["cost_vs_state_activity_median"] = round(amount / state_activity_median, 4)
    else:
        features["cost_vs_state_activity_median"] = None

    if amount is not None and category_median and category_median > 0:
        features["cost_vs_category_median"] = round(amount / category_median, 4)
    else:
        features["cost_vs_category_median"] = None

    if amount is not None and state_category_median and state_category_median > 0:
        features["cost_vs_state_category_median"] = round(amount / state_category_median, 4)
    else:
        features["cost_vs_state_category_median"] = None

    return features


def build_feature_records(projects):
    """Builds the full list of feature records, plus summary stats for printing."""
    sanction_amounts = [safe_parse_number(p.get("sanction_amount")) for p in projects]

    group_statistics = collect_group_statistics(projects, sanction_amounts)
    (
        activity_medians,
        state_activity_medians,
        category_medians,
        state_category_medians,
        activity_sizes,
        state_activity_sizes,
        category_sizes,
        state_category_sizes,
        distribution_stats,
    ) = group_statistics

    feature_records = []
    stats = {
        "valid_sanction_amount": 0,
        "valid_sanction_date": 0,
        "valid_disbursement_ratio": 0,
    }

    for project, amount in zip(projects, sanction_amounts):
        record = copy_preserved_fields(project)

        record.update(compute_date_features(project, amount))
        record.update(compute_group_features(
            project, amount, activity_medians, state_activity_medians,
            category_medians, state_category_medians, activity_sizes,
            state_activity_sizes, category_sizes, state_category_sizes,
            distribution_stats
        ))

        if amount is not None:
            stats["valid_sanction_amount"] += 1
        if record["days_since_sanction"] is not None:
            stats["valid_sanction_date"] += 1
        if record["disbursement_ratio"] is not None:
            stats["valid_disbursement_ratio"] += 1

        feature_records.append(record)

    group_info = {
        "num_activities": len(activity_sizes),
        "num_state_activity_groups": len(state_activity_sizes),
        "num_categories": len(category_sizes),
        "num_state_category_groups": len(state_category_sizes),
        "activity_sizes": list(activity_sizes.values()),
        "state_activity_sizes": list(state_activity_sizes.values()),
        "category_sizes": list(category_sizes.values()),
        "state_category_sizes": list(state_category_sizes.values()),
    }

    return feature_records, stats, group_info


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(projects_count, features_count, stats, group_info, output_path):
    activity_sizes = group_info["activity_sizes"]
    state_activity_sizes = group_info["state_activity_sizes"]
    state_category_sizes = group_info["state_category_sizes"]

    print("\n--- Feature Build Summary ---")
    print(f"Projects processed: {projects_count}")
    print(f"Features written: {features_count}")
    print(f"Projects with valid sanction amount: {stats['valid_sanction_amount']}")
    print(f"Projects with valid sanction date: {stats['valid_sanction_date']}")
    print(f"Projects with valid disbursement ratio: {stats['valid_disbursement_ratio']}")
    print(f"Number of unique activities: {group_info['num_activities']}")
    print(f"Number of state-activity groups: {group_info['num_state_activity_groups']}")
    print(f"Number of work categories: {group_info['num_categories']}")
    print(f"Number of state-category groups: {group_info['num_state_category_groups']}")

    if activity_sizes:
        print(f"Activity group sizes -> min: {min(activity_sizes)}, "
              f"max: {max(activity_sizes)}, median: {statistics.median(activity_sizes)}")
    else:
        print("Activity group sizes -> no groups found")

    if state_activity_sizes:
        print(f"State-activity group sizes -> min: {min(state_activity_sizes)}, "
              f"max: {max(state_activity_sizes)}, "
              f"median: {statistics.median(state_activity_sizes)}")
    else:
        print("State-activity group sizes -> no groups found")

    if state_category_sizes:
        print(f"State-category group sizes -> min: {min(state_category_sizes)}, "
              f"max: {max(state_category_sizes)}, "
              f"median: {statistics.median(state_category_sizes)}")
    else:
        print("State-category group sizes -> no groups found")

    print(f"Output path: {output_path}")

    

def main():
    try:
        projects = load_projects(PROJECTS_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load projects data: {e}")
        sys.exit(1)

    feature_records, stats, group_info = build_feature_records(projects)

    try:
        save_json(feature_records, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    print("SUCCESS: Feature build complete.")
    print_summary(len(projects), len(feature_records), stats, group_info, OUTPUT_PATH)


if __name__ == "__main__":
    main()
    
