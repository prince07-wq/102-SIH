"""
Diagnostics for Expenditure Anomaly V1 design.

Reads data/processed/features.json only. Does not modify anything, does
not implement a detector, and does not write any output files other than
printing to the terminal.

For each of the three candidate signals (expenditure_record_count,
records_per_vendor, average_payment_size), this script resolves the
proposed peer hierarchy (work_stage+normalized_activity_name -> work_stage
-> all expenditure-bearing projects) and reports baseline usage, IQR=0
prevalence, group-level statistic spread, fence-crossing counts, and the
most extreme examples.
"""

import json
import os
import statistics
from collections import defaultdict

FEATURES_PATH = os.path.join("data", "processed", "features.json")

MIN_GROUP_SIZE = 20
MISSING_LABEL = "__MISSING__"


def load_features(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list in features.json")
    return data


def is_missing(value):
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def safe_number(value):
    if is_missing(value):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            return None
    return None


def compute_signal_values(project):
    """Computes the three candidate signal values for one expenditure-bearing project."""
    record_count = safe_number(project.get("expenditure_record_count"))
    vendor_count = safe_number(project.get("unique_vendor_count"))
    total_disbursed = safe_number(project.get("total_disbursed"))

    record_count_value = record_count if (record_count is not None and record_count >= 0) else None

    records_per_vendor_value = None
    if record_count is not None and vendor_count is not None and vendor_count > 0:
        records_per_vendor_value = record_count / vendor_count

    avg_payment_value = None
    if record_count is not None and record_count > 0 and total_disbursed is not None and total_disbursed >= 0:
        avg_payment_value = total_disbursed / record_count

    return {
        "record_count": record_count_value,
        "records_per_vendor": records_per_vendor_value,
        "avg_payment_size": avg_payment_value,
    }


def get_group_keys(project):
    """Returns (stage+activity key, stage-only key) for the peer hierarchy."""
    stage = project.get("work_stage")
    activity = project.get("normalized_activity_name")

    stage_key = stage if not is_missing(stage) else MISSING_LABEL
    activity_key = activity if not is_missing(activity) else MISSING_LABEL

    return (stage_key, activity_key), stage_key


def calculate_quartiles(values):
    """Computes count, q1, median, q3, iqr for a list of values."""
    if not values:
        return None
    if len(values) == 1:
        q1 = q3 = values[0]
    else:
        q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return {
        "count": len(values),
        "q1": q1,
        "median": statistics.median(values),
        "q3": q3,
        "iqr": q3 - q1,
    }


def build_group_stats(projects, signal_name):
    """Builds level1 (stage+activity), level2 (stage), and level3 (all) stats for a signal."""
    level1_values = defaultdict(list)
    level2_values = defaultdict(list)
    level3_values = []

    for project in projects:
        value = project["_signals"][signal_name]
        if value is None:
            continue
        level1_key, level2_key = get_group_keys(project)
        level1_values[level1_key].append(value)
        level2_values[level2_key].append(value)
        level3_values.append(value)

    level1_stats = {k: calculate_quartiles(v) for k, v in level1_values.items()}
    level2_stats = {k: calculate_quartiles(v) for k, v in level2_values.items()}
    level3_stats = calculate_quartiles(level3_values)

    return level1_stats, level2_stats, level3_stats


def resolve_baseline(project, signal_name, level1_stats, level2_stats, level3_stats):
    """Resolves which peer-group level applies to a project for a given signal."""
    value = project["_signals"][signal_name]
    if value is None:
        return None

    level1_key, level2_key = get_group_keys(project)

    l1 = level1_stats.get(level1_key)
    if l1 and l1["count"] >= MIN_GROUP_SIZE:
        return {"level": "work_stage_activity", "stats": l1, "key": ("L1", level1_key)}

    l2 = level2_stats.get(level2_key)
    if l2 and l2["count"] >= MIN_GROUP_SIZE:
        return {"level": "work_stage", "stats": l2, "key": ("L2", level2_key)}

    if level3_stats and level3_stats["count"] >= MIN_GROUP_SIZE:
        return {"level": "all_expenditure_bearing", "stats": level3_stats, "key": ("L3", "ALL")}

    return {"level": "insufficient_data", "stats": None, "key": ("NONE", None)}


def analyze_signal(projects, signal_name, two_sided):
    """Runs the full diagnostic for a single signal and prints the report."""
    level1_stats, level2_stats, level3_stats = build_group_stats(projects, signal_name)

    resolved = []
    for project in projects:
        value = project["_signals"][signal_name]
        if value is None:
            continue
        baseline = resolve_baseline(project, signal_name, level1_stats, level2_stats, level3_stats)
        resolved.append((project, value, baseline))

    total_valid = len(resolved)
    print(f"\n=== Signal: {signal_name} ===")
    print(f"Valid projects for this signal: {total_valid}")

    # Baseline usage counts
    baseline_counts = defaultdict(int)
    for _, _, baseline in resolved:
        baseline_counts[baseline["level"]] += 1
    print("Baseline usage:")
    for level in ["work_stage_activity", "work_stage", "all_expenditure_bearing", "insufficient_data"]:
        print(f"  {level}: {baseline_counts.get(level, 0)}")

    # IQR=0 prevalence
    iqr_zero_count = sum(
        1 for _, _, baseline in resolved
        if baseline["stats"] and baseline["stats"]["iqr"] == 0
    )
    pct = (iqr_zero_count / total_valid * 100) if total_valid else 0.0
    print(f"Projects in IQR=0 peer groups: {iqr_zero_count} ({pct:.2f}%)")

    # Distribution of group-level Q1/median/Q3/IQR across the DISTINCT selected peer groups
    seen_groups = {}
    for _, _, baseline in resolved:
        if baseline["stats"] is None:
            continue
        seen_groups[baseline["key"]] = baseline["stats"]

    print(f"Distinct peer groups actually used: {len(seen_groups)}")
    for stat_name in ["q1", "median", "q3", "iqr"]:
        values = [g[stat_name] for g in seen_groups.values()]
        if values:
            print(
                f"  group-level {stat_name} -> min: {min(values):.2f}, "
                f"median: {statistics.median(values):.2f}, max: {max(values):.2f}"
            )

    # Fence-crossing counts
    above_upper = 0
    above_extreme_upper = 0
    below_lower = 0
    below_extreme_lower = 0

    extremity_list = []  # (extremity, project, value, baseline)

    for project, value, baseline in resolved:
        stats = baseline["stats"]
        if stats is None:
            continue
        q1, q3, iqr = stats["q1"], stats["q3"], stats["iqr"]
        upper_fence = q3 + 1.5 * iqr
        extreme_upper = q3 + 3.0 * iqr
        lower_fence = q1 - 1.5 * iqr
        extreme_lower = q1 - 3.0 * iqr

        if value > upper_fence:
            above_upper += 1
        if value > extreme_upper:
            above_extreme_upper += 1

        if two_sided:
            if value < lower_fence:
                below_lower += 1
            if value < extreme_lower:
                below_extreme_lower += 1
            extremity = max(value - upper_fence, lower_fence - value)
        else:
            extremity = value - upper_fence

        extremity_list.append((extremity, project, value, baseline))

    print(f"Above Q3 + 1.5*IQR: {above_upper}")
    print(f"Above Q3 + 3*IQR: {above_extreme_upper}")
    if two_sided:
        print(f"Below Q1 - 1.5*IQR: {below_lower}")
        print(f"Below Q1 - 3*IQR: {below_extreme_lower}")

    # Top 10 most extreme
    extremity_list.sort(key=lambda x: x[0], reverse=True)
    print("Top 10 most extreme examples:")
    for extremity, project, value, baseline in extremity_list[:10]:
        stats = baseline["stats"]
        print(
            f"  project_id={project.get('project_id')} "
            f"stage={project.get('work_stage')!r} "
            f"activity={project.get('normalized_activity_name')!r} "
            f"value={value:.4f} "
            f"peer_median={stats['median']:.4f} q1={stats['q1']:.4f} q3={stats['q3']:.4f} "
            f"iqr={stats['iqr']:.4f} group_size={stats['count']} baseline={baseline['level']}"
        )


def main():
    projects = load_features(FEATURES_PATH)
    expenditure_projects = [p for p in projects if p.get("has_expenditure")]
    print(f"Total projects: {len(projects)}")
    print(f"Projects with has_expenditure=true: {len(expenditure_projects)}")

    for project in expenditure_projects:
        project["_signals"] = compute_signal_values(project)

    analyze_signal(expenditure_projects, "record_count", two_sided=False)
    analyze_signal(expenditure_projects, "records_per_vendor", two_sided=False)
    analyze_signal(expenditure_projects, "avg_payment_size", two_sided=True)


if __name__ == "__main__":
    main()
    