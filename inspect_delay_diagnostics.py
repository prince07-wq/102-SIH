"""
Diagnostics for Delay Anomaly V1 design.
Reads data/processed/features.json only. Does not modify anything
or write any output files other than printing to the terminal.
"""

import json
import os
import statistics
from collections import Counter, defaultdict
from datetime import date

FEATURES_PATH = os.path.join("data", "processed", "features.json")

# Must match ANALYSIS_DATE in build_features.py / detect_cost_anomalies.py
ANALYSIS_DATE = date(2026, 8, 27)


def load_features(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list in features.json")
    return data


def safe_iso_date(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def describe(values, label):
    values = [v for v in values if v is not None]
    print(f"\n--- {label} ---")
    print(f"count: {len(values)}")
    if not values:
        print("(no valid values)")
        return
    values_sorted = sorted(values)
    print(f"min: {values_sorted[0]}")
    print(f"max: {values_sorted[-1]}")
    print(f"mean: {round(statistics.mean(values), 1)}")
    print(f"median: {statistics.median(values)}")
    if len(values) >= 4:
        q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
        print(f"q1: {round(q1,1)}  q2: {round(q2,1)}  q3: {round(q3,1)}")

    # simple histogram buckets, adjust ranges as needed once you see the scale
    buckets = [0, 30, 90, 180, 365, 730, 1095, float("inf")]
    labels = ["0-30", "31-90", "91-180", "181-365", "366-730", "731-1095", "1095+"]
    counts = Counter()
    for v in values:
        for i in range(len(buckets) - 1):
            if buckets[i] <= v < buckets[i + 1]:
                counts[labels[i]] += 1
                break
    print("distribution:")
    for label_ in labels:
        print(f"  {label_}: {counts.get(label_, 0)}")


def main():
    projects = load_features(FEATURES_PATH)
    print(f"Total projects: {len(projects)}")

    # 1. work_stage value counts
    stage_counts = Counter(p.get("work_stage") for p in projects)
    print("\n--- work_stage value counts ---")
    for stage, count in stage_counts.most_common():
        print(f"  {stage!r}: {count}")

    # 2. days_since_sanction, overall and by work_stage
    describe([p.get("days_since_sanction") for p in projects], "days_since_sanction (all)")

    by_stage = defaultdict(list)
    for p in projects:
        by_stage[p.get("work_stage")].append(p.get("days_since_sanction"))
    for stage, values in by_stage.items():
        describe(values, f"days_since_sanction (work_stage={stage!r})")

    # 3. days_to_first_expenditure
    describe(
        [p.get("days_to_first_expenditure") for p in projects],
        "days_to_first_expenditure",
    )

    # 4. inactivity since last expenditure (derived, has_expenditure only)
    inactivity_days = []
    for p in projects:
        if not p.get("has_expenditure"):
            continue
        last_date = safe_iso_date(p.get("last_expenditure_date"))
        if last_date:
            inactivity_days.append((ANALYSIS_DATE - last_date).days)
    describe(inactivity_days, "days_since_last_expenditure (has_expenditure=true)")

    # 5. work_stage x has_expenditure cross-tab
    print("\n--- work_stage x has_expenditure ---")
    cross = Counter((p.get("work_stage"), p.get("has_expenditure")) for p in projects)
    for (stage, has_exp), count in sorted(cross.items(), key=lambda x: str(x[0])):
        print(f"  work_stage={stage!r}, has_expenditure={has_exp}: {count}")


if __name__ == "__main__":
    main()