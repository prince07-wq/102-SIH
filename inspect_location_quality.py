import json
import random
import re
from collections import Counter

INPUT_FILE = "data/raw/sanctioned.json"
RANDOM_SEED = 42
EXAMPLES_PER_BUCKET = 10


HIGH_PATTERNS = {
    "village": r"\b(village|vilage|vill\.?|gaon|gram)\b",
    "taluk_tehsil": r"\b(tq|taluk|taluka|tehsil|block)\b",
    "locality": r"\b(colony|nagar|mohalla|faliya|pada|para)\b",
}

MEDIUM_PATTERNS = {
    "ward": r"\bward\b",
    "district": r"\b(district|distt?\.?)\b",
    "city_town": r"\b(city|town)\b",
}

LOW_PATTERNS = {
    "road": r"\b(road|rd\.?|street|lane|rasta|cc road|c\.c\.road)\b",
}


def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def matches_any(text, patterns):
    matched = []

    for name, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(name)

    return matched


def classify_location(row):
    description = str(row.get("WORK_DESCRIPTION") or "").strip()
    text = description.lower()

    high = matches_any(text, HIGH_PATTERNS)
    medium = matches_any(text, MEDIUM_PATTERNS)
    low = matches_any(text, LOW_PATTERNS)

    ida = str(row.get("IDA_NAME") or "").strip()
    state = str(row.get("STATE_NAME") or "").strip()
    constituency = str(row.get("CONSTITUENCY") or "").strip()

    has_admin_context = bool(ida and state)
    has_secondary_context = bool(constituency or state)

    # HIGH:
    # strong locality clue plus administrative support
    if high and has_admin_context:
        return "HIGH", high + medium + low

    # HIGH:
    # combination such as ward + city/district/locality
    if len(medium) >= 2 and has_admin_context:
        return "HIGH", high + medium + low

    # MEDIUM:
    # explicit locality clue but incomplete administrative context
    if high and has_secondary_context:
        return "MEDIUM", high + medium + low

    # MEDIUM:
    # ward/district/city with usable broader context
    if medium and has_admin_context:
        return "MEDIUM", high + medium + low

    # LOW:
    # only weak textual location clues such as road
    if low:
        return "LOW", high + medium + low

    return "NONE", []


def print_examples(bucket, rows):
    print("\n" + "=" * 80)
    print(f"{bucket} EXAMPLES")
    print("=" * 80)

    for row in rows:
        print(f"Project ID   : {row['project_id']}")
        print(f"State        : {row['state']}")
        print(f"Constituency : {row['constituency']}")
        print(f"IDA          : {row['ida']}")
        print(f"Signals      : {', '.join(row['signals']) or 'None'}")
        print(f"Description  : {row['description']}")
        print("-" * 80)


def main():
    random.seed(RANDOM_SEED)

    data = load_data()

    bucket_counts = Counter()
    bucket_rows = {
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
        "NONE": [],
    }

    for row in data:
        bucket, signals = classify_location(row)

        bucket_counts[bucket] += 1

        bucket_rows[bucket].append(
            {
                "project_id": row.get("WORK_RECOMMENDATION_DTL_ID"),
                "state": row.get("STATE_NAME"),
                "constituency": row.get("CONSTITUENCY"),
                "ida": row.get("IDA_NAME"),
                "description": str(
                    row.get("WORK_DESCRIPTION") or ""
                ).strip(),
                "signals": signals,
            }
        )

    total = len(data)

    print("=" * 80)
    print("LOCATION QUALITY DIAGNOSTIC")
    print("=" * 80)

    print(f"\nTotal sanctioned records: {total:,}")

    print("\nQuality distribution:")

    for bucket in ["HIGH", "MEDIUM", "LOW", "NONE"]:
        count = bucket_counts[bucket]
        pct = count / total * 100 if total else 0

        print(f"{bucket:8} {count:8,}  ({pct:6.2f}%)")

    attemptable = bucket_counts["HIGH"] + bucket_counts["MEDIUM"]

    attemptable_pct = attemptable / total * 100 if total else 0

    print("\nPotential geocoding candidates:")
    print(
        f"HIGH + MEDIUM: {attemptable:,} / {total:,} "
        f"({attemptable_pct:.2f}%)"
    )

    print("\nRecommended policy:")
    print("HIGH   -> geocode automatically")
    print("MEDIUM -> geocode with stricter validation")
    print("LOW    -> do not automatically geocode")
    print("NONE   -> location unavailable")

    for bucket in ["HIGH", "MEDIUM", "LOW", "NONE"]:
        rows = bucket_rows[bucket]

        sample_size = min(EXAMPLES_PER_BUCKET, len(rows))

        examples = random.sample(rows, sample_size) if rows else []

        print_examples(bucket, examples)


if __name__ == "__main__":
    main()
    