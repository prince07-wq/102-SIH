"""
Diagnostics for Duplicate/Similarity Anomaly V1 design (progressive levels).

Reads data/processed/features.json only. Does not modify anything, does
not implement scoring, and does not label anything as fraud or confirmed
duplication -- these are candidate repeated-project patterns requiring
human review.

Levels (each progressively narrower, refining the previous level's groups):
  A. same normalized work_description
  B. A + same state_name + constituency
  C. B + same sanction_amount
  D. C + same ida_name
  E. D + same sanction_date

Exact matching only -- no fuzzy/similarity logic, no invented thresholds
beyond the specific day-windows requested for reporting (0/7/30/90 days),
which are descriptive buckets, not a scoring cutoff.
"""

import json
import os
import re
import statistics
from collections import defaultdict
from itertools import combinations
from datetime import date

FEATURES_PATH = os.path.join("data", "processed", "features.json")

MISSING = "__MISSING__"

# Normalized (post lowercase/punctuation-strip) descriptions treated as
# unusable/generic placeholders rather than real project descriptions.
GENERIC_DESCRIPTIONS = {
    "",
    "na",
    "n a",
    "nil",
    "none",
    "not applicable",
    "as per attachment",
    "as per attechment",
    "as per enclosed",
    "as per enclosure",
    "as per annexure",
    "details attached",
    "see attachment",
}

MIN_USABLE_DESCRIPTION_LENGTH = 4


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
    """Lowercases, strips punctuation, collapses whitespace. No fuzzy logic."""
    if is_missing(text) or not isinstance(text, str):
        return None
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else None


def is_generic(normalized):
    """Flags empty/placeholder/too-short descriptions as unusable for duplicate analysis."""
    if normalized is None:
        return True
    if normalized in GENERIC_DESCRIPTIONS:
        return True
    if len(normalized) < MIN_USABLE_DESCRIPTION_LENGTH:
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


def safe_iso_date(value):
    if is_missing(value) or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def describe(values, label):
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


def build_level_a(projects):
    """Level A: group by normalized description, keep groups of size >= 2."""
    buckets = defaultdict(list)
    for p in projects:
        norm = p["_normalized_description"]
        if not is_generic(norm):
            buckets[norm].append(p)
    return [{"description": desc, "projects": plist} for desc, plist in buckets.items() if len(plist) >= 2]


def refine(groups, key_func):
    """Splits each group's projects further by key_func, keeping subgroups of size >= 2."""
    refined = []
    for group in groups:
        buckets = defaultdict(list)
        for p in group["projects"]:
            buckets[key_func(p)].append(p)
        for plist in buckets.values():
            if len(plist) >= 2:
                refined.append({"description": group["description"], "projects": plist})
    return refined


def state_constituency_key(p):
    state = p.get("state_name") if not is_missing(p.get("state_name")) else MISSING
    constituency = p.get("constituency") if not is_missing(p.get("constituency")) else MISSING
    return (state, constituency)


def amount_key(p):
    amount = safe_number(p.get("sanction_amount"))
    return round(amount, 2) if amount is not None else f"{MISSING}_{id(p)}"  # unique -> never groups


def ida_key(p):
    return p.get("ida_name") if not is_missing(p.get("ida_name")) else f"{MISSING}_{id(p)}"


def date_key(p):
    parsed = safe_iso_date(p.get("sanction_date"))
    return parsed.isoformat() if parsed else f"{MISSING}_{id(p)}"


def print_sample(p):
    print(
        f"      project_id={p.get('project_id')} amount={p.get('sanction_amount')} "
        f"date={p.get('sanction_date')} constituency={p.get('constituency')!r} "
        f"ida_name={p.get('ida_name')!r} activity={p.get('normalized_activity_name')!r}"
    )


def report_level(level_name, groups, show_top=False, top_n=15):
    num_groups = len(groups)
    num_projects = sum(len(g["projects"]) for g in groups)
    sizes = [len(g["projects"]) for g in groups]

    print(f"\n=== Level {level_name} ===")
    print(f"Groups: {num_groups}")
    print(f"Projects involved: {num_projects}")
    describe(sizes, "Group-size distribution:")

    if show_top and groups:
        top_groups = sorted(groups, key=lambda g: len(g["projects"]), reverse=True)[:top_n]
        print(f"\nTop {min(top_n, len(top_groups))} groups at level {level_name}:")
        for group in top_groups:
            print(f"\n  Description: {group['description']!r}")
            print(f"  Occurrences: {len(group['projects'])}")
            for p in group["projects"][:8]:
                print_sample(p)


def report_date_diffs(level_d_groups):
    """Reports pairwise sanction_date differences (in days) between projects within each D group."""
    diffs = []
    for group in level_d_groups:
        dated_projects = [
            (p, safe_iso_date(p.get("sanction_date")))
            for p in group["projects"]
        ]
        dated_projects = [(p, d) for p, d in dated_projects if d is not None]
        for (_, date_a), (_, date_b) in combinations(dated_projects, 2):
            diffs.append(abs((date_a - date_b).days))

    describe(diffs, "Pairwise sanction_date difference (days) within Level D groups:")

    print("\nPairwise date-difference counts (cumulative windows):")
    for window in [0, 7, 30, 90]:
        count = sum(1 for d in diffs if d <= window)
        print(f"  within {window} days: {count}")


def main():
    projects = load_features(FEATURES_PATH)
    print(f"Total projects: {len(projects)}")

    for p in projects:
        p["_normalized_description"] = normalize_description(p.get("work_description"))

    generic_count = sum(
        1 for p in projects
        if p["_normalized_description"] is None or is_generic(p["_normalized_description"])
    )
    print(f"Projects excluded as unusable/generic descriptions: {generic_count}")

    level_a = build_level_a(projects)
    report_level("A (same description)", level_a, show_top=False)

    level_b = refine(level_a, state_constituency_key)
    report_level("B (A + state + constituency)", level_b, show_top=False)

    level_c = refine(level_b, amount_key)
    report_level("C (B + sanction_amount)", level_c, show_top=True)

    level_d = refine(level_c, ida_key)
    report_level("D (C + ida_name)", level_d, show_top=True)

    print("\n--- Level D date-proximity diagnostics ---")
    report_date_diffs(level_d)

    level_e = refine(level_d, date_key)
    report_level("E (D + sanction_date)", level_e, show_top=True)


if __name__ == "__main__":
    main()