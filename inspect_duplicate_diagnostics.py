"""
Diagnostics for Duplicate/Similarity Anomaly V1 design.

Reads data/processed/features.json only. Does not modify anything,
does not implement a detector, and does not invent any thresholds.

Uses EXACT matching on a normalized work_description only (lowercase,
punctuation stripped, whitespace collapsed) -- not fuzzy/similarity
matching -- since a similarity threshold would need to be a deliberate
design decision, not something inferred from this script.

normalized_activity_name is NOT used as a duplication signal; it is only
shown as context in the top-repeated-description samples.
"""

import json
import os
import re
import statistics
from collections import defaultdict, Counter
from datetime import date

FEATURES_PATH = os.path.join("data", "processed", "features.json")


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


def normalize_description(text):
    """Lowercases, strips punctuation, and collapses whitespace. No stemming/fuzzy logic."""
    if is_missing(text) or not isinstance(text, str):
        return None
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else None


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


def safe_iso_date(value):
    if is_missing(value) or not isinstance(value, str):
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
    print(f"min: {values_sorted[0]:.2f}")
    print(f"max: {values_sorted[-1]:.2f}")
    print(f"mean: {statistics.mean(values):.2f}")
    print(f"median: {statistics.median(values):.2f}")
    if len(values) >= 4:
        q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
        print(f"q1: {q1:.2f}  q2: {q2:.2f}  q3: {q3:.2f}")


def main():
    projects = load_features(FEATURES_PATH)
    print(f"Total projects: {len(projects)}")

    for p in projects:
        p["_normalized_description"] = normalize_description(p.get("work_description"))

    valid_desc_count = sum(1 for p in projects if p["_normalized_description"] is not None)
    print(f"Projects with a usable normalized description: {valid_desc_count}")

    # --- 1. Exact duplicate normalized descriptions (national level) ---
    national_groups = defaultdict(list)
    for p in projects:
        if p["_normalized_description"] is not None:
            national_groups[p["_normalized_description"]].append(p)

    group_sizes = [len(v) for v in national_groups.values()]
    duplicate_groups = {k: v for k, v in national_groups.items() if len(v) >= 2}
    projects_in_duplicates = sum(len(v) for v in duplicate_groups.values())

    print(f"\nDistinct normalized descriptions: {len(national_groups)}")
    print(f"Descriptions appearing more than once (duplicate groups): {len(duplicate_groups)}")
    print(f"Projects belonging to a duplicate group: {projects_in_duplicates} "
          f"({projects_in_duplicates / valid_desc_count * 100:.2f}% of projects with a description)")

    describe(group_sizes, "Normalized description group sizes (frequency distribution)")

    # --- 2. Duplicates within the same state ---
    state_groups = defaultdict(list)
    for p in projects:
        if p["_normalized_description"] is not None:
            state_key = p.get("state_name") if not is_missing(p.get("state_name")) else "__MISSING__"
            state_groups[(p["_normalized_description"], state_key)].append(p)
    state_duplicate_groups = {k: v for k, v in state_groups.items() if len(v) >= 2}
    state_duplicate_projects = sum(len(v) for v in state_duplicate_groups.values())
    print(f"\nDescription+state duplicate groups: {len(state_duplicate_groups)}")
    print(f"Projects in a description+state duplicate group: {state_duplicate_projects}")

    # --- 3. Duplicates within the same constituency (scoped by state to avoid name collisions) ---
    constituency_groups = defaultdict(list)
    for p in projects:
        if p["_normalized_description"] is not None:
            state_key = p.get("state_name") if not is_missing(p.get("state_name")) else "__MISSING__"
            const_key = p.get("constituency") if not is_missing(p.get("constituency")) else "__MISSING__"
            constituency_groups[(p["_normalized_description"], state_key, const_key)].append(p)
    constituency_duplicate_groups = {k: v for k, v in constituency_groups.items() if len(v) >= 2}
    constituency_duplicate_projects = sum(len(v) for v in constituency_duplicate_groups.values())
    print(f"\nDescription+constituency duplicate groups: {len(constituency_duplicate_groups)}")
    print(f"Projects in a description+constituency duplicate group: {constituency_duplicate_projects}")

    # --- 4. Sanction amount spread within duplicate groups ---
    amount_ratios = []
    for group in duplicate_groups.values():
        amounts = [safe_number(p.get("sanction_amount")) for p in group]
        amounts = [a for a in amounts if a is not None and a > 0]
        if len(amounts) >= 2:
            amount_ratios.append(max(amounts) / min(amounts))
    describe(amount_ratios, "Sanction amount max/min ratio within duplicate-description groups")

    # --- 5. Sanction date proximity within duplicate groups ---
    date_spans_days = []
    for group in duplicate_groups.values():
        dates = [safe_iso_date(p.get("sanction_date")) for p in group]
        dates = [d for d in dates if d is not None]
        if len(dates) >= 2:
            date_spans_days.append((max(dates) - min(dates)).days)
    describe(date_spans_days, "Sanction date span (days) within duplicate-description groups")

    # --- 6. Implementing authority (IDA) overlap within duplicate groups ---
    distinct_ida_counts = []
    single_ida_group_count = 0
    for group in duplicate_groups.values():
        ida_values = {p.get("ida_name") for p in group if not is_missing(p.get("ida_name"))}
        if ida_values:
            distinct_ida_counts.append(len(ida_values))
            if len(ida_values) == 1:
                single_ida_group_count += 1
    describe(distinct_ida_counts, "Distinct implementing-authority (ida_name) count per duplicate group")
    if distinct_ida_counts:
        pct_single = single_ida_group_count / len(distinct_ida_counts) * 100
        print(f"Duplicate groups with a single implementing authority: {single_ida_group_count} "
              f"({pct_single:.2f}%)")

    # --- 7. Top repeated descriptions with contextual samples ---
    top_groups = sorted(duplicate_groups.items(), key=lambda kv: len(kv[1]), reverse=True)[:15]
    print("\n--- Top 15 most repeated normalized descriptions ---")
    for description, group in top_groups:
        activities = Counter(p.get("normalized_activity_name") for p in group)
        states = Counter(p.get("state_name") for p in group)
        idas = Counter(p.get("ida_name") for p in group)
        print(f"\nDescription: {description!r}")
        print(f"  Occurrences: {len(group)}")
        print(f"  Distinct states: {len(states)}  |  Distinct activities: {len(activities)}  "
              f"|  Distinct IDAs: {len(idas)}")
        print("  Sample projects:")
        for p in group[:5]:
            print(
                f"    project_id={p.get('project_id')} state={p.get('state_name')!r} "
                f"constituency={p.get('constituency')!r} ida_name={p.get('ida_name')!r} "
                f"sanction_amount={p.get('sanction_amount')} sanction_date={p.get('sanction_date')} "
                f"normalized_activity_name={p.get('normalized_activity_name')!r}"
            )


if __name__ == "__main__":
    main()
    