"""
scripts/detect_delay_anomalies.py

Produces an explainable, rule-based delay-anomaly score for every project
in data/processed/features.json.

Three branches:
  - work_stage == "Work Completed" -> excluded from delay scoring.
  - incomplete + no expenditure     -> "stalled_start" signal, using
                                        days_since_sanction.
  - incomplete + has expenditure    -> "stalled_execution" signal, using
                                        days_since_last_expenditure
                                        (derived from last_expenditure_date).

For each signal, projects are compared against a peer group using this
hierarchy (falling through when a level is too small):
  work_stage + normalized_activity_name (>= MIN_GROUP_SIZE)
  -> work_stage (>= MIN_GROUP_SIZE)
  -> signal-wide cohort (>= MIN_GROUP_SIZE)
  -> insufficient_data

Scoring reuses the same IQR-fence method as detect_cost_anomalies.py for
consistency. This is NOT machine learning and does NOT compute an overall
risk score.
"""

import json
import math
import os
import sys
import statistics
from collections import Counter, defaultdict
from datetime import date

FEATURES_PATH = os.path.join("data", "processed", "features.json")
OUTPUT_PATH = os.path.join("data", "processed", "delay_anomalies.json")

# Must match ANALYSIS_DATE in build_features.py / detect_cost_anomalies.py
ANALYSIS_DATE = date(2026, 8, 27)

MIN_GROUP_SIZE = 20
FLAG_THRESHOLD = 50

COMPLETED_STAGE_LABEL = "work completed"

MISSING_GROUP_LABEL = "__MISSING__"

# Piecewise linear breakpoints for the IQR-zero ratio fallback, identical
# to the ones used in detect_cost_anomalies.py for consistency.
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


def safe_iso_date(value):
    """Parses an ISO 'YYYY-MM-DD' string into a date object. Returns None if missing/invalid."""
    if is_missing(value) or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def is_completed_stage(work_stage):
    """Checks (case/whitespace-insensitively) whether a work_stage means the work is done."""
    if is_missing(work_stage) or not isinstance(work_stage, str):
        return False
    return work_stage.strip().lower() == COMPLETED_STAGE_LABEL


def determine_signal(project):
    """Assigns each project to exactly one branch: completed, stalled_start, or stalled_execution."""
    if is_completed_stage(project.get("work_stage")):
        return "completed"
    if project.get("has_expenditure"):
        return "stalled_execution"
    return "stalled_start"


def compute_duration(project, signal):
    """
    Computes the applicable duration-in-days value for a project's signal.

    Returns (duration_days, is_valid). A duration is considered invalid
    (not usable for scoring or group statistics) if the underlying date
    is missing/unparseable, or if the computed duration would be negative
    -- negative/malformed durations must never contribute to a score.
    """
    if signal == "stalled_start":
        value = project.get("days_since_sanction")
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
            return int(value), True
        return None, False

    if signal == "stalled_execution":
        last_date = safe_iso_date(project.get("last_expenditure_date"))
        if last_date is None:
            return None, False
        delta_days = (ANALYSIS_DATE - last_date).days
        if delta_days >= 0:
            return delta_days, True
        return None, False

    return None, False  # "completed" branch has no duration to score.


def get_group_keys(project, signal):
    """Returns the three peer-group keys (stage+activity, stage, signal-wide) for a project."""
    stage = project.get("work_stage")
    activity = project.get("normalized_activity_name")

    stage_key = stage if not is_missing(stage) else MISSING_GROUP_LABEL
    activity_key = activity if not is_missing(activity) else MISSING_GROUP_LABEL

    stage_activity_key = (signal, stage_key, activity_key)
    stage_only_key = (signal, stage_key)
    signal_key = signal

    return stage_activity_key, stage_only_key, signal_key


def calculate_quartiles(values):
    """Computes count, q1, median, q3, and iqr for a list of duration values."""
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


def build_project_computations(projects):
    """First pass: determines signal and duration validity for every project."""
    computed = []
    for project in projects:
        signal = determine_signal(project)
        if signal == "completed":
            computed.append({"signal": signal, "duration": None, "valid": False})
            continue
        duration, valid = compute_duration(project, signal)
        computed.append({"signal": signal, "duration": duration, "valid": valid})
    return computed


def collect_group_stats(projects, computed):
    """
    Second pass: groups valid durations by each hierarchy level and computes
    quartile statistics per group. Only projects with a valid duration
    contribute -- this keeps group "size" meaningful for the >= MIN_GROUP_SIZE
    checks, since a group padded with unusable values would misrepresent how
    much real comparison data actually backs the baseline.
    """
    stage_activity_values = defaultdict(list)
    stage_values = defaultdict(list)
    signal_values = defaultdict(list)

    for project, comp in zip(projects, computed):
        if comp["signal"] == "completed" or not comp["valid"]:
            continue

        stage_activity_key, stage_key, signal_key = get_group_keys(project, comp["signal"])
        stage_activity_values[stage_activity_key].append(comp["duration"])
        stage_values[stage_key].append(comp["duration"])
        signal_values[signal_key].append(comp["duration"])

    stage_activity_stats = {k: calculate_quartiles(v) for k, v in stage_activity_values.items()}
    stage_stats = {k: calculate_quartiles(v) for k, v in stage_values.items()}
    signal_stats = {k: calculate_quartiles(v) for k, v in signal_values.items()}

    return stage_activity_stats, stage_stats, signal_stats


def choose_baseline(project, signal, duration_valid, stage_activity_stats, stage_stats, signal_stats):
    """
    Picks the most specific peer group with enough members, per the
    confirmed hierarchy: work_stage+activity -> work_stage -> signal-wide
    -> insufficient_data.
    """
    if signal == "completed":
        return {"baseline": "completed", "group_size": 0, "stats": None, "scope_description": None}

    if not duration_valid:
        return {"baseline": "invalid_duration", "group_size": 0, "stats": None, "scope_description": None}

    stage_activity_key, stage_key, signal_key = get_group_keys(project, signal)

    stage_activity = stage_activity_stats.get(stage_activity_key)
    if stage_activity and stage_activity["count"] >= MIN_GROUP_SIZE:
        return {
            "baseline": "work_stage_activity",
            "group_size": stage_activity["count"],
            "stats": stage_activity,
            "scope_description": "at the same work stage and activity type",
        }

    stage_only = stage_stats.get(stage_key)
    if stage_only and stage_only["count"] >= MIN_GROUP_SIZE:
        return {
            "baseline": "work_stage",
            "group_size": stage_only["count"],
            "stats": stage_only,
            "scope_description": "at the same work stage",
        }

    signal_wide = signal_stats.get(signal_key)
    if signal_wide and signal_wide["count"] >= MIN_GROUP_SIZE:
        return {
            "baseline": "signal_wide",
            "group_size": signal_wide["count"],
            "stats": signal_wide,
            "scope_description": "across all comparable delay cases",
        }

    fallback_size = max(
        stage_activity["count"] if stage_activity else 0,
        stage_only["count"] if stage_only else 0,
        signal_wide["count"] if signal_wide else 0,
    )
    return {"baseline": "insufficient_data", "group_size": fallback_size, "stats": None, "scope_description": None}


def iqr_to_score(value, q3, iqr):
    """Converts a duration's position beyond Q3 into a continuous, capped IQR score."""
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


def ratio_to_score(ratio):
    """
    Converts a duration ratio (value / median) into a 0-100 score using the
    same piecewise linear breakpoints as detect_cost_anomalies.py, used only
    as the IQR-zero fallback.
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


def format_days(value):
    """Formats a day count for reason text."""
    return f"{value:g}"


def build_reason(signal, baseline_info, duration, upper_fence, scoring_method):
    """Builds a human-readable, neutral explanation that names the actual baseline used."""
    baseline = baseline_info["baseline"]

    if baseline == "completed":
        return "This project's work stage is marked Work Completed, so delay scoring does not apply."

    if baseline == "invalid_duration":
        if signal == "stalled_start":
            return "Sanction date is missing or invalid, so days since sanction could not be calculated."
        return "Last expenditure date is missing or invalid, so days since last expenditure could not be calculated."

    if baseline == "insufficient_data":
        return (
            f"Comparison group is too small (only {baseline_info['group_size']} "
            f"comparable project(s)) to reliably assess delay for this project."
        )

    scope = baseline_info["scope_description"]
    group_size = baseline_info["group_size"]
    stats = baseline_info["stats"]
    q3 = stats["q3"]

    signal_label = (
        "days since sanction with no recorded expenditure"
        if signal == "stalled_start"
        else "days since the last recorded expenditure"
    )

    if scoring_method == "median_ratio_iqr_zero":
        return (
            f"The peer group's duration IQR is zero because comparable projects {scope} "
            f"have identical or tightly repeated durations. Since {format_days(duration)} "
            f"{signal_label} exceeds Q3, the score uses the median-ratio method for "
            f"{group_size} comparable projects {scope}."
        )

    if duration > upper_fence:
        return (
            f"{format_days(duration)} {signal_label} exceeds the upper delay fence of "
            f"{format_days(upper_fence)} days for {group_size} comparable projects {scope}."
        )

    if duration > q3:
        return (
            f"{format_days(duration)} {signal_label} is above the typical (Q3) range but does not "
            f"exceed the upper delay fence of {format_days(upper_fence)} days for {group_size} "
            f"comparable projects {scope}."
        )

    return (
        f"{format_days(duration)} {signal_label} is at or below the typical (Q3) range for "
        f"{group_size} comparable projects {scope}."
    )


def compute_delay_anomaly(project, signal, duration, duration_valid, baseline_info):
    """Computes the full delay-anomaly result dict for a single project."""
    upper_fence = None
    extreme_fence = None
    ratio = None
    q1 = median = q3 = iqr = None

    if baseline_info["baseline"] in ("completed", "invalid_duration", "insufficient_data"):
        score = 0.0
        scoring_method = baseline_info["baseline"]
    else:
        stats = baseline_info["stats"]
        q1, median, q3, iqr = stats["q1"], stats["median"], stats["q3"], stats["iqr"]
        upper_fence = q3 + 1.5 * iqr
        extreme_fence = q3 + 3.0 * iqr

        if iqr == 0 and duration > q3:
            if median and median > 0:
                ratio = round(duration / median, 4)
                score = ratio_to_score(ratio)
                scoring_method = "median_ratio_iqr_zero"
            else:
                score = 0.0
                scoring_method = "insufficient_data"
        elif iqr > 0:
            score = iqr_to_score(duration, q3, iqr)
            scoring_method = "iqr"
        else:
            # iqr == 0 and duration <= q3: project matches the (identical) peer values.
            score = 0.0
            scoring_method = "iqr"

    flagged = score >= FLAG_THRESHOLD
    reason = build_reason(signal, baseline_info, duration, upper_fence, scoring_method)

    return {
        "project_id": project.get("project_id"),
        "delay": {
            "score": score,
            "flagged": flagged,
            "signal": signal,
            "work_stage": project.get("work_stage"),
            "value_days": duration,
            "baseline": baseline_info["baseline"],
            "comparison_group_size": baseline_info["group_size"],
            "q1_days": q1,
            "median_days": median,
            "q3_days": q3,
            "iqr_days": iqr,
            "upper_fence_days": upper_fence,
            "extreme_fence_days": extreme_fence,
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
    signal_counts = Counter(r["delay"]["signal"] for r in results)
    baseline_counts = Counter(r["delay"]["baseline"] for r in results)
    scoring_method_counts = Counter(r["delay"]["scoring_method"] for r in results)
    flagged_count = sum(1 for r in results if r["delay"]["flagged"])
    score_buckets = Counter(bucket_score(r["delay"]["score"]) for r in results)

    top_20 = sorted(results, key=lambda r: r["delay"]["score"], reverse=True)[:20]

    return {
        "signal_counts": signal_counts,
        "baseline_counts": baseline_counts,
        "scoring_method_counts": scoring_method_counts,
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
    print("\n--- Delay Anomaly Detection Summary ---")
    print(f"Projects processed: {projects_count}")

    print("\nSignal breakdown:")
    for signal in ["completed", "stalled_start", "stalled_execution"]:
        print(f"  {signal}: {stats['signal_counts'].get(signal, 0)}")

    print("\nBaseline used:")
    for baseline in ["work_stage_activity", "work_stage", "signal_wide", "insufficient_data",
                      "invalid_duration", "completed"]:
        print(f"  {baseline}: {stats['baseline_counts'].get(baseline, 0)}")

    print("\nScoring method:")
    for method in ["iqr", "median_ratio_iqr_zero", "insufficient_data", "invalid_duration", "completed"]:
        print(f"  {method}: {stats['scoring_method_counts'].get(method, 0)}")

    print(f"\nFlagged count (score >= {FLAG_THRESHOLD}): {stats['flagged_count']}")
    flagged_percentage = (stats["flagged_count"] / projects_count * 100) if projects_count else 0.0
    print(f"Flagged percentage: {flagged_percentage:.2f}%")

    print("\nScore distribution:")
    for bucket in ["0-19", "20-49", "50-79", "80-100"]:
        print(f"  {bucket}: {stats['score_buckets'].get(bucket, 0)}")

    print("\nTop 20 highest-scoring projects:")
    for r in stats["top_20"]:
        d = r["delay"]
        print(
            f"  {r['project_id']}: score={d['score']} signal={d['signal']} baseline={d['baseline']} "
            f"value_days={d['value_days']} q3_days={d['q3_days']} upper_fence_days={d['upper_fence_days']}"
        )

    print(f"\nOutput path: {output_path}")


def main():
    try:
        projects = load_features(FEATURES_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load features data: {e}")
        sys.exit(1)

    computed = build_project_computations(projects)
    stage_activity_stats, stage_stats, signal_stats = collect_group_stats(projects, computed)

    results = []
    for project, comp in zip(projects, computed):
        baseline_info = choose_baseline(
            project, comp["signal"], comp["valid"],
            stage_activity_stats, stage_stats, signal_stats
        )
        results.append(
            compute_delay_anomaly(project, comp["signal"], comp["duration"], comp["valid"], baseline_info)
        )

    try:
        save_json(results, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    stats = build_summary_stats(results)

    print("SUCCESS: Delay anomaly detection complete.")
    print_summary(len(results), stats, OUTPUT_PATH)


if __name__ == "__main__":
    main()