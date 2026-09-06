"""
scripts/detect_cost_anomalies.py

Produces an explainable, rule-based cost-anomaly score for every project
in data/processed/features.json, comparing each project's sanction
amount against its activity or category peer group median, preferring
more specific state-level groups when they have enough projects.

This is NOT machine learning and does NOT compute an overall risk score.
"""

import json
import math
import os
import sys
from collections import Counter

FEATURES_PATH = os.path.join("data", "processed", "features.json")
OUTPUT_PATH = os.path.join("data", "processed", "cost_anomalies.json")

MIN_GROUP_SIZE = 20
FLAG_THRESHOLD = 50

# Piecewise linear breakpoints for converting a cost ratio into a 0-100
# score: (ratio, score). Between points, score is linearly interpolated.
# Beyond the final breakpoint, score is capped at 100.
SCORE_BREAKPOINTS = [
    (1.25, 0),
    (1.5, 20),
    (2.0, 50),
    (3.0, 80),
    (5.0, 100),
]


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
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            return None
    return None


def ratio_to_score(ratio):
    """
    Converts a cost ratio into a 0-100 score using piecewise linear
    interpolation between SCORE_BREAKPOINTS. Ratios at or below the first
    breakpoint score 0; ratios at or above the last breakpoint score 100.
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


def choose_baseline(project):
    """
    Decides which comparison group to use for a project, per the confirmed
    preference order: state+activity, activity, state+category, category
    (each if group size >= 20), else insufficient data.

    Returns a dict describing the chosen baseline, or None-baseline info
    if no group qualifies.
    """
    state_activity_size = project.get("state_activity_group_size") or 0
    activity_size = project.get("activity_group_size") or 0
    state_category_size = project.get("state_category_group_size") or 0
    category_size = project.get("category_group_size") or 0

    if state_activity_size >= MIN_GROUP_SIZE:
        return {
            "baseline": "state_activity",
            "group_size": state_activity_size,
            "ratio": project.get("cost_vs_state_activity_median"),
            "median": project.get("state_activity_median_sanction_amount"),
            "q1": project.get("state_activity_q1_sanction_amount"),
            "q3": project.get("state_activity_q3_sanction_amount"),
            "iqr": project.get("state_activity_iqr_sanction_amount"),
            "scope_description": "with the same state and activity type",
        }

    if activity_size >= MIN_GROUP_SIZE:
        return {
            "baseline": "activity",
            "group_size": activity_size,
            "ratio": project.get("cost_vs_activity_median"),
            "median": project.get("activity_median_sanction_amount"),
            "q1": project.get("activity_q1_sanction_amount"),
            "q3": project.get("activity_q3_sanction_amount"),
            "iqr": project.get("activity_iqr_sanction_amount"),
            "scope_description": "with the same activity type nationwide",
        }

    if state_category_size >= MIN_GROUP_SIZE:
        return {
            "baseline": "state_category",
            "group_size": state_category_size,
            "ratio": project.get("cost_vs_state_category_median"),
            "median": project.get("state_category_median_sanction_amount"),
            "q1": project.get("state_category_q1_sanction_amount"),
            "q3": project.get("state_category_q3_sanction_amount"),
            "iqr": project.get("state_category_iqr_sanction_amount"),
            "scope_description": "with the same state and work category",
        }

    if category_size >= MIN_GROUP_SIZE:
        return {
            "baseline": "category",
            "group_size": category_size,
            "ratio": project.get("cost_vs_category_median"),
            "median": project.get("category_median_sanction_amount"),
            "q1": project.get("category_q1_sanction_amount"),
            "q3": project.get("category_q3_sanction_amount"),
            "iqr": project.get("category_iqr_sanction_amount"),
            "scope_description": "with the same work category nationwide",
        }

    return {
        "baseline": "insufficient_data",
        "group_size": max(
            state_activity_size,
            activity_size,
            state_category_size,
            category_size,
        ),
        "ratio": None,
        "median": None,
        "q1": None,
        "q3": None,
        "iqr": None,
        "scope_description": None,
    }


def iqr_to_score(project_cost, q3, iqr):
    """Converts cost position beyond Q3 into a continuous, capped IQR score."""
    upper_fence = q3 + 1.5 * iqr
    extreme_fence = q3 + 3.0 * iqr

    if project_cost <= q3:
        return 0.0

    if project_cost <= upper_fence:
        fraction = (project_cost - q3) / (upper_fence - q3)
        return round(49.0 * fraction, 2)

    if project_cost <= extreme_fence:
        fraction = (project_cost - upper_fence) / (extreme_fence - upper_fence)
        return round(50.0 + 29.0 * fraction, 2)

    excess = project_cost - extreme_fence
    score = 80.0 + 20.0 * (1.0 - math.exp(-excess / (3.0 * iqr)))
    return round(min(score, 100.0), 2)


def format_amount(value):
    """Formats a numeric amount as whole Indian rupees for explanations."""
    return f"₹{value:,.0f}"


def build_reason(baseline_info, sanction_amount, q3, upper_fence, scoring_method):
    """Builds a human-readable, neutral explanation for the score."""
    baseline = baseline_info["baseline"]

    if baseline == "insufficient_data":
        return (
            f"Comparison group is too small (only {baseline_info['group_size']} "
            f"comparable project(s)) to reliably assess this project's cost."
        )

    if scoring_method == "insufficient_data":
        return (
            "Sanction amount or comparison distribution is unavailable for this project, "
            "so a cost comparison could not be calculated."
        )

    if sanction_amount is None or q3 is None:
        return (
            "Sanction amount or comparison distribution is unavailable for this project, "
            "so a cost comparison could not be calculated."
        )

    scope = baseline_info["scope_description"]
    group_size = baseline_info["group_size"]

    if scoring_method == "median_ratio_iqr_zero":
        return (
            f"The peer-group IQR is zero because comparable projects have identical "
            f"or tightly repeated costs. Since the sanction amount {format_amount(sanction_amount)} "
            f"exceeds Q3, the score uses the existing median-ratio method for {group_size} "
            f"comparable projects {scope}."
        )

    if sanction_amount > upper_fence:
        return (
            f"Sanction amount {format_amount(sanction_amount)} exceeds the upper cost fence "
            f"of {format_amount(upper_fence)} for {group_size} comparable projects {scope}."
        )

    if sanction_amount > q3:
        return (
            f"Sanction amount {format_amount(sanction_amount)} is above Q3 but does not exceed "
            f"the upper cost fence of {format_amount(upper_fence)} for {group_size} "
            f"comparable projects {scope}."
        )

    return (
        f"Sanction amount {format_amount(sanction_amount)} is at or below Q3 for "
        f"{group_size} comparable projects {scope}."
    )


def compute_cost_anomaly(project):
    """Computes the full cost-anomaly result dict for a single project."""
    sanction_amount = safe_number(project.get("sanction_amount"))
    baseline_info = choose_baseline(project)

    ratio = safe_number(baseline_info["ratio"])
    median = safe_number(baseline_info["median"])
    q1 = safe_number(baseline_info["q1"])
    q3 = safe_number(baseline_info["q3"])
    iqr = safe_number(baseline_info["iqr"])
    upper_fence = None
    extreme_fence = None

    if (
        baseline_info["baseline"] == "insufficient_data"
        or sanction_amount is None
        or q1 is None
        or q3 is None
        or iqr is None
        or iqr < 0
    ):
        score = 0.0
        scoring_method = "insufficient_data"
    else:
        upper_fence = q3 + 1.5 * iqr
        extreme_fence = q3 + 3.0 * iqr

        if iqr == 0 and sanction_amount > q3:
            if ratio is not None:
                score = ratio_to_score(ratio)
                scoring_method = "median_ratio_iqr_zero"
            else:
                score = 0.0
                scoring_method = "insufficient_data"
        else:
            score = iqr_to_score(sanction_amount, q3, iqr) if iqr > 0 else 0.0
            scoring_method = "iqr"

    flagged = score >= FLAG_THRESHOLD
    reason = build_reason(
        baseline_info,
        sanction_amount,
        q3,
        upper_fence,
        scoring_method,
    )

    return {
        "project_id": project.get("project_id"),
        "cost": {
            "score": score,
            "flagged": flagged,
            "baseline": baseline_info["baseline"],
            "comparison_group_size": baseline_info["group_size"],
            "project_sanction_amount": sanction_amount,
            "q1_sanction_amount": q1,
            "median_sanction_amount": median,
            "q3_sanction_amount": q3,
            "iqr": iqr,
            "upper_fence": upper_fence,
            "extreme_fence": extreme_fence,
            "scoring_method": scoring_method,
            "ratio": ratio,
            "reason": reason,
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
    baseline_counts = Counter(r["cost"]["baseline"] for r in results)
    flagged_count = sum(1 for r in results if r["cost"]["flagged"])
    score_buckets = Counter(bucket_score(r["cost"]["score"]) for r in results)
    scoring_method_counts = Counter(r["cost"]["scoring_method"] for r in results)

    top_20 = sorted(results, key=lambda r: r["cost"]["score"], reverse=True)[:20]

    return {
        "state_activity_used": baseline_counts.get("state_activity", 0),
        "activity_used": baseline_counts.get("activity", 0),
        "state_category_used": baseline_counts.get("state_category", 0),
        "category_used": baseline_counts.get("category", 0),
        "insufficient_data": baseline_counts.get("insufficient_data", 0),
        "iqr_scoring_count": scoring_method_counts.get("iqr", 0),
        "iqr_zero_fallback_count": scoring_method_counts.get("median_ratio_iqr_zero", 0),
        "insufficient_scoring_count": scoring_method_counts.get("insufficient_data", 0),
        "flagged_count": flagged_count,
        "score_buckets": score_buckets,
        "top_20": top_20,
    }


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(projects_count, stats, output_path):
    print("\n--- Cost Anomaly Detection Summary ---")
    print(f"Projects processed: {projects_count}")
    print(f"State-activity baseline used: {stats['state_activity_used']}")
    print(f"Activity fallback used: {stats['activity_used']}")
    print(f"State-category baseline used: {stats['state_category_used']}")
    print(f"Category fallback used: {stats['category_used']}")
    print(f"Insufficient-data baseline used: {stats['insufficient_data']}")
    print(f"IQR scoring count: {stats['iqr_scoring_count']}")
    print(f"IQR-zero fallback count: {stats['iqr_zero_fallback_count']}")
    print(f"Insufficient-data count: {stats['insufficient_scoring_count']}")
    print(f"Flagged count (score >= {FLAG_THRESHOLD}): {stats['flagged_count']}")
    flagged_percentage = (
        stats["flagged_count"] / projects_count * 100 if projects_count else 0.0
    )
    print(f"Flagged percentage: {flagged_percentage:.2f}%")

    print("\nScore distribution:")
    for bucket in ["0-19", "20-49", "50-79", "80-100"]:
        print(f"  {bucket}: {stats['score_buckets'].get(bucket, 0)}")

    print("\nTop 20 highest-scoring projects:")
    for r in stats["top_20"]:
        c = r["cost"]
        print(
            f"  {r['project_id']}: score={c['score']} baseline={c['baseline']} "
            f"project_cost={c['project_sanction_amount']} q1={c['q1_sanction_amount']} "
            f"median={c['median_sanction_amount']} q3={c['q3_sanction_amount']} "
            f"iqr={c['iqr']} upper_fence={c['upper_fence']}"
        )

    print(f"\nOutput path: {output_path}")


def main():
    try:
        projects = load_features(FEATURES_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load features data: {e}")
        sys.exit(1)

    results = [compute_cost_anomaly(project) for project in projects]

    try:
        save_json(results, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    stats = build_summary_stats(results)

    print("SUCCESS: Cost anomaly detection complete.")
    print_summary(len(results), stats, OUTPUT_PATH)


if __name__ == "__main__":
    main()

