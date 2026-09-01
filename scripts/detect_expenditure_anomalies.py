"""
scripts/detect_expenditure_anomalies.py

Produces an explainable, rule-based expenditure-anomaly score for every
project in data/processed/features.json.

Evaluated only for projects with has_expenditure=true. Three signals:
  1. payment_count               = expenditure_record_count            (upper-tail)
  2. repeated_vendor_payments    = expenditure_record_count / unique_vendor_count (upper-tail)
  3. stage_expenditure_mismatch  = fixed score 50 when work_stage == "Sanction"
                                    but expenditure already exists

Signals 1 and 2 use the same peer hierarchy, IQR-fence scoring, and
zero-IQR median-ratio fallback already used by detect_cost_anomalies.py.
The final expenditure score is the max of the three signal scores.

Projects without expenditure are marked not_applicable (score 0), NOT
"safe" or "normal" -- stalled starts are Delay Anomaly V1's responsibility.

This is NOT machine learning and does NOT compute an overall risk score.
Cost V1, Delay V1, and feature generation are not modified by this script.
"""

import json
import math
import os
import sys
import statistics
from collections import Counter, defaultdict

FEATURES_PATH = os.path.join("data", "processed", "features.json")
OUTPUT_PATH = os.path.join("data", "processed", "expenditure_anomalies.json")

MIN_GROUP_SIZE = 20
FLAG_THRESHOLD = 50
MISSING_LABEL = "__MISSING__"
STAGE_MISMATCH_SCORE = 50.0

# Piecewise linear breakpoints for the IQR-zero ratio fallback, identical
# to the ones used in detect_cost_anomalies.py for consistency.
SCORE_BREAKPOINTS = [
    (1.25, 0),
    (1.5, 20),
    (2.0, 50),
    (3.0, 80),
    (5.0, 100),
]

SCOPE_DESCRIPTIONS = {
    "work_stage_activity": "at the same work stage and activity type",
    "work_stage": "at the same work stage",
    "all_expenditure_bearing": "across all expenditure-bearing projects",
}

SIGNAL_LABELS = {
    "payment_count": "the number of expenditure payment records",
    "repeated_vendor_payments": "expenditure payments per vendor",
}


def load_features(filepath):
    """Loads features.json and validates that its top-level structure is a list."""
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


def safe_number(value):
    """Safely parses a numeric value that may already be a number or a string. Returns float or None."""
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


def ratio_to_score(ratio):
    """
    Converts a value/median ratio into a 0-100 score using piecewise linear
    interpolation between SCORE_BREAKPOINTS, matching detect_cost_anomalies.py.
    """
    if ratio <= SCORE_BREAKPOINTS[0][0]:
        return 0.0
    if ratio >= SCORE_BREAKPOINTS[-1][0]:
        return 100.0
    for (r_low, s_low), (r_high, s_high) in zip(SCORE_BREAKPOINTS, SCORE_BREAKPOINTS[1:]):
        if r_low <= ratio <= r_high:
            fraction = (ratio - r_low) / (r_high - r_low)
            return round(s_low + fraction * (s_high - s_low), 2)
    return 100.0  # Safety fallback; should not be reached.


def iqr_to_score(value, q3, iqr):
    """Converts a value's position beyond Q3 into a continuous, capped IQR score."""
    upper_fence = q3 + 1.5 * iqr
    extreme_fence = q3 + 3.0 * iqr

    if value <= q3:
        return 0.0

    if value <= upper_fence:
        fraction = (value - q3) / (upper_fence - q3)
        return round(49.0 * fraction, 2)

    if value <= extreme_fence:
        fraction = (value - upper_fence) / (extreme_fence - upper_fence)
        return round(50.0 + 29.0 * fraction, 2)

    excess = value - extreme_fence
    score = 80.0 + 20.0 * (1.0 - math.exp(-excess / (3.0 * iqr)))
    return round(min(score, 100.0), 2)


def is_sanction_stage(work_stage):
    """Checks (case/whitespace-insensitively) whether a work_stage is 'Sanction'."""
    if is_missing(work_stage) or not isinstance(work_stage, str):
        return False
    return work_stage.strip().lower() == "sanction"


def compute_signal_values(project):
    """Computes payment_count and repeated_vendor_payments for one expenditure-bearing project."""
    record_count = safe_number(project.get("expenditure_record_count"))
    vendor_count = safe_number(project.get("unique_vendor_count"))

    payment_count_value = record_count if (record_count is not None and record_count >= 0) else None

    repeated_vendor_payments_value = None
    if record_count is not None and vendor_count is not None and vendor_count > 0:
        repeated_vendor_payments_value = record_count / vendor_count

    return {
        "payment_count": payment_count_value,
        "repeated_vendor_payments": repeated_vendor_payments_value,
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


def build_group_stats(expenditure_projects, signal_name):
    """Builds level1 (stage+activity), level2 (stage), and level3 (all) stats for a signal."""
    level1_values = defaultdict(list)
    level2_values = defaultdict(list)
    level3_values = []

    for project in expenditure_projects:
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
        return {"baseline": "invalid_value", "stats": None, "group_size": 0, "scope_description": None}

    level1_key, level2_key = get_group_keys(project)

    level1 = level1_stats.get(level1_key)
    if level1 and level1["count"] >= MIN_GROUP_SIZE:
        return {
            "baseline": "work_stage_activity",
            "stats": level1,
            "group_size": level1["count"],
            "scope_description": SCOPE_DESCRIPTIONS["work_stage_activity"],
        }

    level2 = level2_stats.get(level2_key)
    if level2 and level2["count"] >= MIN_GROUP_SIZE:
        return {
            "baseline": "work_stage",
            "stats": level2,
            "group_size": level2["count"],
            "scope_description": SCOPE_DESCRIPTIONS["work_stage"],
        }

    if level3_stats and level3_stats["count"] >= MIN_GROUP_SIZE:
        return {
            "baseline": "all_expenditure_bearing",
            "stats": level3_stats,
            "group_size": level3_stats["count"],
            "scope_description": SCOPE_DESCRIPTIONS["all_expenditure_bearing"],
        }

    fallback_size = max(
        level1["count"] if level1 else 0,
        level2["count"] if level2 else 0,
        level3_stats["count"] if level3_stats else 0,
    )
    return {"baseline": "insufficient_data", "stats": None, "group_size": fallback_size, "scope_description": None}


def build_signal_reason(signal_name, value, baseline_info, q3, upper_fence, scoring_method):
    """Builds a human-readable, neutral explanation for one signal's score."""
    label = SIGNAL_LABELS[signal_name]
    baseline = baseline_info["baseline"]

    if baseline == "invalid_value":
        return f"{label.capitalize()} could not be computed for this project."

    if baseline == "insufficient_data":
        return (
            f"Comparison group is too small (only {baseline_info['group_size']} "
            f"comparable project(s)) to assess {label}."
        )

    if scoring_method == "insufficient_data":
        return f"{label.capitalize()} or its comparison distribution is unavailable for this project."

    scope = baseline_info["scope_description"]
    group_size = baseline_info["group_size"]

    if scoring_method == "median_ratio_iqr_zero":
        return (
            f"The peer-group IQR for {label} is zero because comparable projects {scope} have "
            f"identical or tightly repeated values. Since this project's value ({value:g}) exceeds "
            f"Q3, the score uses the median-ratio method for {group_size} comparable projects {scope}."
        )

    if value > upper_fence:
        return (
            f"{label.capitalize()} ({value:g}) exceeds the upper fence of {upper_fence:.2f} "
            f"for {group_size} comparable projects {scope}."
        )

    if value > q3:
        return (
            f"{label.capitalize()} ({value:g}) is above Q3 but does not exceed the upper fence "
            f"of {upper_fence:.2f} for {group_size} comparable projects {scope}."
        )

    return f"{label.capitalize()} ({value:g}) is at or below Q3 for {group_size} comparable projects {scope}."


def build_signal_result(signal_name, value, baseline_info):
    """Computes the full result dict and numeric score for one IQR-based signal."""
    q1 = median = q3 = iqr = upper_fence = extreme_fence = ratio = None

    if baseline_info["baseline"] in ("invalid_value", "insufficient_data"):
        score = 0.0
        scoring_method = baseline_info["baseline"]
    else:
        stats = baseline_info["stats"]
        q1, median, q3, iqr = stats["q1"], stats["median"], stats["q3"], stats["iqr"]
        upper_fence = q3 + 1.5 * iqr
        extreme_fence = q3 + 3.0 * iqr

        if iqr == 0 and value > q3:
            if median and median > 0:
                ratio = round(value / median, 4)
                score = ratio_to_score(ratio)
                scoring_method = "median_ratio_iqr_zero"
            else:
                score = 0.0
                scoring_method = "insufficient_data"
        elif iqr > 0:
            score = iqr_to_score(value, q3, iqr)
            scoring_method = "iqr"
        else:
            score = 0.0
            scoring_method = "iqr"

    reason = build_signal_reason(signal_name, value, baseline_info, q3, upper_fence, scoring_method)

    result = {
        "score": score,
        "value": value,
        "baseline": baseline_info["baseline"],
        "comparison_group_size": baseline_info["group_size"],
        "q1": q1,
        "median": median,
        "q3": q3,
        "iqr": iqr,
        "upper_fence": upper_fence,
        "extreme_fence": extreme_fence,
        "scoring_method": scoring_method,
        "ratio": ratio,
        "reason": reason,
    }
    return result, score


def build_stage_mismatch_result(project):
    """Computes the fixed-score stage/expenditure workflow-mismatch signal."""
    work_stage = project.get("work_stage")
    triggered = is_sanction_stage(work_stage) and bool(project.get("has_expenditure"))
    score = STAGE_MISMATCH_SCORE if triggered else 0.0

    if triggered:
        reason = (
            "Work stage is recorded as 'Sanction' but expenditure already exists for this "
            "project. This may reflect workflow/status lag and requires review."
        )
    else:
        reason = "Work stage and expenditure status show no workflow/status lag for this signal."

    result = {
        "score": score,
        "triggered": triggered,
        "work_stage": work_stage,
        "reason": reason,
    }
    return result, score


def evaluate_expenditure_project(project, pc_level1, pc_level2, pc_level3, rvp_level1, rvp_level2, rvp_level3):
    """Computes the full expenditure-anomaly result for a project with has_expenditure=true."""
    pc_baseline = resolve_baseline(project, "payment_count", pc_level1, pc_level2, pc_level3)
    pc_result, pc_score = build_signal_result(
        "payment_count", project["_signals"]["payment_count"], pc_baseline
    )

    rvp_baseline = resolve_baseline(project, "repeated_vendor_payments", rvp_level1, rvp_level2, rvp_level3)
    rvp_result, rvp_score = build_signal_result(
        "repeated_vendor_payments", project["_signals"]["repeated_vendor_payments"], rvp_baseline
    )

    mismatch_result, mismatch_score = build_stage_mismatch_result(project)

    candidates = [
        ("payment_count", pc_score, pc_result["reason"]),
        ("repeated_vendor_payments", rvp_score, rvp_result["reason"]),
        ("stage_expenditure_mismatch", mismatch_score, mismatch_result["reason"]),
    ]
    strongest_signal, final_score, overall_reason = max(candidates, key=lambda c: c[1])

    flagged = final_score >= FLAG_THRESHOLD

    return {
        "project_id": project.get("project_id"),
        "expenditure": {
            "score": final_score,
            "flagged": flagged,
            "status": "evaluated",
            "strongest_signal": strongest_signal,
            "reason": overall_reason,
            "signals": {
                "payment_count": pc_result,
                "repeated_vendor_payments": rvp_result,
                "stage_expenditure_mismatch": mismatch_result,
            },
        },
    }


def evaluate_not_applicable_project(project):
    """Builds the not_applicable result for a project with no recorded expenditure."""
    reason = (
        "This project has no recorded expenditure, so expenditure-based anomaly signals "
        "do not apply. Stalled-start assessment is handled separately by Delay Anomaly V1."
    )
    placeholder_signal = {
        "score": 0.0,
        "value": None,
        "baseline": "not_applicable",
        "comparison_group_size": 0,
        "q1": None,
        "median": None,
        "q3": None,
        "iqr": None,
        "upper_fence": None,
        "extreme_fence": None,
        "scoring_method": "not_applicable",
        "ratio": None,
        "reason": reason,
    }
    mismatch_placeholder = {
        "score": 0.0,
        "triggered": False,
        "work_stage": project.get("work_stage"),
        "reason": reason,
    }

    return {
        "project_id": project.get("project_id"),
        "expenditure": {
            "score": 0.0,
            "flagged": False,
            "status": "not_applicable",
            "strongest_signal": None,
            "reason": reason,
            "signals": {
                "payment_count": dict(placeholder_signal),
                "repeated_vendor_payments": dict(placeholder_signal),
                "stage_expenditure_mismatch": mismatch_placeholder,
            },
        },
    }


def bucket_score(score):
    """Returns which display bucket a score falls into."""
    if score < 20:
        return "0-19"
    if score < 50:
        return "20-49"
    if score < 80:
        return "50-79"
    return "80-100"


def build_summary_stats(results):
    """Computes counters and distributions needed for the terminal summary."""
    evaluated = [r for r in results if r["expenditure"]["status"] == "evaluated"]
    not_applicable = [r for r in results if r["expenditure"]["status"] == "not_applicable"]

    pc_baseline_counts = Counter(r["expenditure"]["signals"]["payment_count"]["baseline"] for r in evaluated)
    rvp_baseline_counts = Counter(
        r["expenditure"]["signals"]["repeated_vendor_payments"]["baseline"] for r in evaluated
    )

    pc_method_counts = Counter(r["expenditure"]["signals"]["payment_count"]["scoring_method"] for r in evaluated)
    rvp_method_counts = Counter(
        r["expenditure"]["signals"]["repeated_vendor_payments"]["scoring_method"] for r in evaluated
    )

    stage_mismatch_count = sum(
        1 for r in evaluated if r["expenditure"]["signals"]["stage_expenditure_mismatch"]["triggered"]
    )

    flagged_count = sum(1 for r in results if r["expenditure"]["flagged"])
    score_buckets = Counter(bucket_score(r["expenditure"]["score"]) for r in results)

    top_10_flagged = sorted(
        (r for r in results if r["expenditure"]["flagged"]),
        key=lambda r: r["expenditure"]["score"],
        reverse=True,
    )[:10]

    return {
        "evaluated_count": len(evaluated),
        "not_applicable_count": len(not_applicable),
        "pc_baseline_counts": pc_baseline_counts,
        "rvp_baseline_counts": rvp_baseline_counts,
        "pc_method_counts": pc_method_counts,
        "rvp_method_counts": rvp_method_counts,
        "stage_mismatch_count": stage_mismatch_count,
        "flagged_count": flagged_count,
        "score_buckets": score_buckets,
        "top_10_flagged": top_10_flagged,
    }


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(projects_count, stats, output_path):
    print("\n--- Expenditure Anomaly Detection Summary ---")
    print(f"Total projects: {projects_count}")
    print(f"Evaluated (has_expenditure=true): {stats['evaluated_count']}")
    print(f"Not applicable (no expenditure): {stats['not_applicable_count']}")

    print("\nBaseline usage - payment_count:")
    for level in ["work_stage_activity", "work_stage", "all_expenditure_bearing", "insufficient_data"]:
        print(f"  {level}: {stats['pc_baseline_counts'].get(level, 0)}")

    print("\nBaseline usage - repeated_vendor_payments:")
    for level in ["work_stage_activity", "work_stage", "all_expenditure_bearing", "insufficient_data"]:
        print(f"  {level}: {stats['rvp_baseline_counts'].get(level, 0)}")

    print("\nScoring method - payment_count:")
    for method in ["iqr", "median_ratio_iqr_zero", "insufficient_data"]:
        print(f"  {method}: {stats['pc_method_counts'].get(method, 0)}")

    print("\nScoring method - repeated_vendor_payments:")
    for method in ["iqr", "median_ratio_iqr_zero", "insufficient_data"]:
        print(f"  {method}: {stats['rvp_method_counts'].get(method, 0)}")

    print(f"\nStage/expenditure mismatches (Sanction stage with expenditure): {stats['stage_mismatch_count']}")

    print(f"\nFlagged count (score >= {FLAG_THRESHOLD}): {stats['flagged_count']}")
    flagged_percentage = (stats["flagged_count"] / projects_count * 100) if projects_count else 0.0
    print(f"Flagged percentage: {flagged_percentage:.2f}%")

    print("\nScore distribution:")
    for bucket in ["0-19", "20-49", "50-79", "80-100"]:
        print(f"  {bucket}: {stats['score_buckets'].get(bucket, 0)}")

    print("\nTop 10 flagged projects:")
    for r in stats["top_10_flagged"]:
        e = r["expenditure"]
        print(f"  {r['project_id']}: score={e['score']} strongest_signal={e['strongest_signal']}")

    print(f"\nOutput path: {output_path}")


def main():
    try:
        projects = load_features(FEATURES_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load features data: {e}")
        sys.exit(1)

    expenditure_projects = [p for p in projects if p.get("has_expenditure")]
    not_applicable_projects = [p for p in projects if not p.get("has_expenditure")]

    for project in expenditure_projects:
        project["_signals"] = compute_signal_values(project)

    pc_level1, pc_level2, pc_level3 = build_group_stats(expenditure_projects, "payment_count")
    rvp_level1, rvp_level2, rvp_level3 = build_group_stats(expenditure_projects, "repeated_vendor_payments")

    results = []
    for project in expenditure_projects:
        results.append(
            evaluate_expenditure_project(
                project, pc_level1, pc_level2, pc_level3, rvp_level1, rvp_level2, rvp_level3
            )
        )
    for project in not_applicable_projects:
        results.append(evaluate_not_applicable_project(project))

    try:
        save_json(results, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    stats = build_summary_stats(results)

    print("SUCCESS: Expenditure anomaly detection complete.")
    print_summary(len(results), stats, OUTPUT_PATH)


if __name__ == "__main__":
    main()
    