"""
Diagnostics for Expenditure Anomaly V1 design.
Reads data/processed/features.json only. Does not modify anything
or write any output files other than printing to the terminal.
"""

import json
import os
import statistics
from collections import Counter, defaultdict

FEATURES_PATH = os.path.join("data", "processed", "features.json")


def load_features(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list in features.json")
    return data


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
    print(f"mean: {round(statistics.mean(values), 4)}")
    print(f"median: {statistics.median(values)}")
    if len(values) >= 4:
        q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
        print(f"q1: {round(q1,4)}  q2: {round(q2,4)}  q3: {round(q3,4)}")


def main():
    projects = load_features(FEATURES_PATH)
    print(f"Total projects: {len(projects)}")

    with_expenditure = [p for p in projects if p.get("has_expenditure")]
    print(f"Projects with expenditure: {len(with_expenditure)}")

    # 1. disbursement_ratio distribution + threshold counts
    ratios = [p.get("disbursement_ratio") for p in projects if p.get("disbursement_ratio") is not None]
    describe(ratios, "disbursement_ratio (all valid)")
    for threshold in [1.0, 1.5, 2.0, 3.0]:
        count = sum(1 for r in ratios if r > threshold)
        print(f"  disbursement_ratio > {threshold}: {count}")

    # 2. expenditure_record_count, overall and by work_stage
    describe(
        [p.get("expenditure_record_count") for p in with_expenditure],
        "expenditure_record_count (has_expenditure=true)",
    )
    by_stage = defaultdict(list)
    for p in with_expenditure:
        by_stage[p.get("work_stage")].append(p.get("expenditure_record_count"))
    for stage, values in by_stage.items():
        describe(values, f"expenditure_record_count (work_stage={stage!r})")

    # 3. expenditure_frequency
    describe(
        [p.get("expenditure_frequency") for p in with_expenditure],
        "expenditure_frequency",
    )

    # 4. unique_vendor_count and records-per-vendor
    describe(
        [p.get("unique_vendor_count") for p in with_expenditure],
        "unique_vendor_count",
    )
    records_per_vendor = []
    for p in with_expenditure:
        count = p.get("expenditure_record_count")
        vendors = p.get("unique_vendor_count")
        if count is not None and vendors:
            records_per_vendor.append(count / vendors)
    describe(records_per_vendor, "records_per_vendor (record_count / unique_vendor_count)")

    # 5. average payment size
    avg_payment = []
    for p in with_expenditure:
        total = p.get("total_disbursed")
        count = p.get("expenditure_record_count")
        if total is not None and count:
            avg_payment.append(total / count)
    describe(avg_payment, "average_payment_size (total_disbursed / record_count)")

    # 6. inconsistency check: expenditure records exist but total_disbursed <= 0
    zero_disbursed_with_records = sum(
        1 for p in with_expenditure if (p.get("total_disbursed") or 0) <= 0
    )
    print(f"\nProjects with expenditure records but total_disbursed <= 0: {zero_disbursed_with_records}")

    # 7. work_stage x (disbursement_ratio > 1) cross-tab
    print("\n--- work_stage x disbursement_ratio>1 ---")
    cross = Counter()
    for p in projects:
        ratio = p.get("disbursement_ratio")
        over = ratio is not None and ratio > 1.0
        cross[(p.get("work_stage"), over)] += 1
    for (stage, over), count in sorted(cross.items(), key=lambda x: str(x[0])):
        print(f"  work_stage={stage!r}, ratio>1={over}: {count}")


if __name__ == "__main__":
    main()