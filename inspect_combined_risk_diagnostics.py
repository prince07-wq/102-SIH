"""
inspect_combined_risk_diagnostics.py

Reads the four frozen anomaly detector outputs, joins them by project_id,
and reports cross-detector diagnostics only.

Inputs (read-only):
  data/processed/cost_anomalies.json
  data/processed/delay_anomalies.json
  data/processed/expenditure_anomalies.json
  data/processed/duplicate_anomalies.json

This is a DIAGNOSTIC ONLY. It does not compute a combined risk score,
does not assign weights, and does not modify any of the four detectors
or their output files.
"""

import json
import math
import os
import statistics
from collections import Counter, defaultdict
from itertools import combinations

COST_PATH = os.path.join("data", "processed", "cost_anomalies.json")
DELAY_PATH = os.path.join("data", "processed", "delay_anomalies.json")
EXPENDITURE_PATH = os.path.join("data", "processed", "expenditure_anomalies.json")
DUPLICATE_PATH = os.path.join("data", "processed", "duplicate_anomalies.json")

DETECTOR_NAMES = ["cost", "delay", "expenditure", "duplicate"]


def load_json_list(filepath):
    """Loads a JSON file and validates that its top-level structure is a list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {filepath}, got {type(data).__name__}")
    return data


def extract_score_flagged(record, nested_key):
    """
    Extracts (score, flagged) from a detector record. cost/delay/expenditure
    nest their fields under a named sub-object; duplicate is flat.
    """
    if nested_key is not None:
        sub = record.get(nested_key, {})
        return sub.get("score"), sub.get("flagged")
    return record.get("score"), record.get("flagged")


def index_by_project_id(records, nested_key):
    """
    Builds project_id -> (score, flagged) and reports duplicate/missing IDs.
    Returns (index, duplicate_id_count, missing_id_count).
    """
    index = {}
    duplicate_count = 0
    missing_count = 0

    for record in records:
        project_id = record.get("project_id")
        if project_id is None:
            missing_count += 1
            continue
        if project_id in index:
            duplicate_count += 1
            continue
        score, flagged = extract_score_flagged(record, nested_key)
        index[project_id] = (score, flagged)

    return index, duplicate_count, missing_count


def describe(values, label):
    """Prints count/min/max/mean/median/quartiles for a list of numeric values."""
    values = [v for v in values if v is not None]
    print(f"\n{label}")
    print(f"  count: {len(values)}")
    if not values:
        print("  (no valid values)")
        return
    values_sorted = sorted(values)
    print(f"  min: {values_sorted[0]:.2f}  max: {values_sorted[-1]:.2f}  "
          f"mean: {statistics.mean(values):.2f}  median: {statistics.median(values):.2f}")
    if len(values) >= 4:
        q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
        print(f"  q1: {q1:.2f}  q2: {q2:.2f}  q3: {q3:.2f}")


def bucket_score(score):
    """Returns which display bucket a score falls into."""
    if score is None:
        return "MISSING"
    if score < 20:
        return "0-19"
    if score < 50:
        return "20-49"
    if score < 80:
        return "50-79"
    return "80-100"


def pearson_correlation(xs, ys):
    """Computes the Pearson correlation coefficient between two equal-length numeric lists."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 2:
        return None, len(pairs)

    x_values = [p[0] for p in pairs]
    y_values = [p[1] for p in pairs]

    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    x_variance = sum((x - x_mean) ** 2 for x in x_values)
    y_variance = sum((y - y_mean) ** 2 for y in y_values)

    denominator = math.sqrt(x_variance * y_variance)
    if denominator == 0:
        return None, len(pairs)

    return numerator / denominator, len(pairs)


def report_record_validation(raw_records, indices):
    """Reports basic ID hygiene: counts, duplicates, missing IDs, and cross-file ID overlap."""
    print("=== Record / ID Validation ===")
    for name in DETECTOR_NAMES:
        records, duplicate_count, missing_count = raw_records[name]
        print(f"  {name}: {len(records)} records, {duplicate_count} duplicate project_id(s), "
              f"{missing_count} missing project_id")

    id_sets = {name: set(indices[name].keys()) for name in DETECTOR_NAMES}
    all_ids = set.union(*id_sets.values())
    common_ids = set.intersection(*id_sets.values())

    print(f"\n  Union of all project_ids across files: {len(all_ids)}")
    print(f"  Intersection (present in all 4 files): {len(common_ids)}")

    for name in DETECTOR_NAMES:
        missing_from_this = all_ids - id_sets[name]
        if missing_from_this:
            print(f"  project_ids missing from {name}: {len(missing_from_this)}")

    return common_ids


def build_joined_table(common_ids, indices):
    """Builds project_id -> {detector_name: (score, flagged)} restricted to common_ids."""
    joined = {}
    for project_id in common_ids:
        joined[project_id] = {name: indices[name][project_id] for name in DETECTOR_NAMES}
    return joined


def report_per_detector_stats(joined):
    print("\n=== Per-Detector Stats ===")
    for name in DETECTOR_NAMES:
        scores = [v[name][0] for v in joined.values()]
        flags = [v[name][1] for v in joined.values()]

        flagged_count = sum(1 for f in flags if f)
        total = len(flags)
        pct = (flagged_count / total * 100) if total else 0.0

        print(f"\n--- {name} ---")
        print(f"  flagged: {flagged_count} / {total} ({pct:.2f}%)")
        describe(scores, "  score distribution:")

        buckets = Counter(bucket_score(s) for s in scores)
        print("  score buckets:")
        for bucket in ["0-19", "20-49", "50-79", "80-100", "MISSING"]:
            if buckets.get(bucket, 0):
                print(f"    {bucket}: {buckets[bucket]}")


def report_flag_count_overlap(joined):
    print("\n=== Flagged-By-N-Detectors Overlap ===")
    flag_count_distribution = Counter()
    for record in joined.values():
        n_flagged = sum(1 for name in DETECTOR_NAMES if record[name][1])
        flag_count_distribution[n_flagged] += 1

    for n in range(0, 5):
        print(f"  flagged by exactly {n} detector(s): {flag_count_distribution.get(n, 0)}")


def report_nonzero_combinations(joined):
    print("\n=== Non-Zero Detector Score Combinations ===")
    combo_counts = Counter()
    for record in joined.values():
        nonzero = tuple(sorted(name for name in DETECTOR_NAMES if (record[name][0] or 0) > 0))
        combo_counts[nonzero] += 1

    for combo, count in sorted(combo_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        label = " + ".join(combo) if combo else "(none)"
        print(f"  {label}: {count}")


def report_pairwise_flag_overlap(joined):
    print("\n=== Pairwise Flag Overlaps ===")
    for a, b in combinations(DETECTOR_NAMES, 2):
        a_flagged = {pid for pid, r in joined.items() if r[a][1]}
        b_flagged = {pid for pid, r in joined.items() if r[b][1]}
        both = a_flagged & b_flagged
        only_a = a_flagged - b_flagged
        only_b = b_flagged - a_flagged
        print(f"  {a} & {b}: both={len(both)}, only_{a}={len(only_a)}, only_{b}={len(only_b)}")


def report_score_correlations(joined):
    print("\n=== Pearson Score Correlations ===")
    for a, b in combinations(DETECTOR_NAMES, 2):
        a_scores = [r[a][0] for r in joined.values()]
        b_scores = [r[b][0] for r in joined.values()]
        corr, n = pearson_correlation(a_scores, b_scores)
        if corr is None:
            print(f"  {a} vs {b}: undefined (n={n})")
        else:
            print(f"  {a} vs {b}: r={corr:.4f} (n={n})")


def report_max_score_by_flag_count(joined):
    print("\n=== Max-Score Distribution by Number of Flagged Detectors ===")
    grouped = defaultdict(list)
    for record in joined.values():
        n_flagged = sum(1 for name in DETECTOR_NAMES if record[name][1])
        max_score = max((record[name][0] or 0) for name in DETECTOR_NAMES)
        grouped[n_flagged].append(max_score)

    for n in range(0, 5):
        if n in grouped:
            describe(grouped[n], f"  flagged by {n} detector(s):")


def report_top_multi_detector(joined, top_n=20):
    print(f"\n=== Top {top_n} Strongest Multi-Detector Projects ===")
    ranked = []
    for project_id, record in joined.items():
        n_flagged = sum(1 for name in DETECTOR_NAMES if record[name][1])
        score_sum = sum((record[name][0] or 0) for name in DETECTOR_NAMES)
        ranked.append((n_flagged, score_sum, project_id, record))

    ranked.sort(key=lambda x: (-x[0], -x[1]))

    for n_flagged, score_sum, project_id, record in ranked[:top_n]:
        scores_str = ", ".join(f"{name}={record[name][0]}" for name in DETECTOR_NAMES)
        print(f"  project_id={project_id} flagged_by={n_flagged} score_sum={score_sum:.2f}  ({scores_str})")


def main():
    raw_records = {}
    indices = {}

    for name, path, nested_key in [
        ("cost", COST_PATH, "cost"),
        ("delay", DELAY_PATH, "delay"),
        ("expenditure", EXPENDITURE_PATH, "expenditure"),
        ("duplicate", DUPLICATE_PATH, None),
    ]:
        records = load_json_list(path)
        index, duplicate_count, missing_count = index_by_project_id(records, nested_key)
        raw_records[name] = (records, duplicate_count, missing_count)
        indices[name] = index

    common_ids = report_record_validation(raw_records, indices)
    joined = build_joined_table(common_ids, indices)

    report_per_detector_stats(joined)
    report_flag_count_overlap(joined)
    report_nonzero_combinations(joined)
    report_pairwise_flag_overlap(joined)
    report_score_correlations(joined)
    report_max_score_by_flag_count(joined)
    report_top_multi_detector(joined, top_n=20)


if __name__ == "__main__":
    main()