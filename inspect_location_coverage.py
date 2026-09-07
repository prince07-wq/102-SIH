import json
import re
from collections import Counter

INPUT_FILE = "data/raw/sanctioned.json"


PATTERNS = {
    "village": r"\b(village|vilage|vill\.?)\b",
    "taluk_tehsil": r"\b(tq|taluk|taluka|tehsil)\b",
    "ward": r"\bward\b",
    "district": r"\b(district|distt?\.?)\b",
    "city_town": r"\b(city|town)\b",
    "colony": r"\b(colony|nagar)\b",
    "road": r"\b(road|rd\.?|street|lane)\b",
    "school_college": r"\b(school|college)\b",
}


def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = load_data()

    total = len(data)
    pattern_counts = Counter()
    usable_location = 0
    attach_count = 0
    file_status_count = 0
    ida_counter = Counter()

    examples = []

    for row in data:
        description = str(row.get("WORK_DESCRIPTION") or "").strip()
        text = description.lower()

        matched = []

        for name, pattern in PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                pattern_counts[name] += 1
                matched.append(name)

        # Simple first-pass rule:
        # at least one useful locality/admin clue in the description
        useful_signals = {
            "village",
            "taluk_tehsil",
            "ward",
            "district",
            "city_town",
            "colony",
            "road",
        }

        if useful_signals.intersection(matched):
            usable_location += 1

            if len(examples) < 20:
                examples.append(
                    {
                        "project_id": row.get("WORK_RECOMMENDATION_DTL_ID"),
                        "state": row.get("STATE_NAME"),
                        "constituency": row.get("CONSTITUENCY"),
                        "ida": row.get("IDA_NAME"),
                        "description": description,
                        "signals": matched,
                    }
                )

        if row.get("ATTACH_ID") is not None:
            attach_count += 1

        if row.get("FILE_STATUS") is not None:
            file_status_count += 1

        ida = str(row.get("IDA_NAME") or "").strip()
        if ida:
            ida_counter[ida] += 1

    print("=" * 70)
    print("LOCATION COVERAGE DIAGNOSTIC")
    print("=" * 70)

    print(f"\nTotal sanctioned records: {total:,}")

    print("\nLocation keyword coverage:")
    for name in PATTERNS:
        count = pattern_counts[name]
        pct = (count / total * 100) if total else 0
        print(f"{name:15} {count:8,}  ({pct:6.2f}%)")

    usable_pct = (usable_location / total * 100) if total else 0

    print("\nEstimated geocodable descriptions:")
    print(f"{usable_location:,} / {total:,} ({usable_pct:.2f}%)")

    print("\nAttachment coverage:")
    print(f"ATTACH_ID present : {attach_count:,}")
    print(f"FILE_STATUS present: {file_status_count:,}")

    print("\nTop 20 implementing authorities:")
    for ida, count in ida_counter.most_common(20):
        print(f"{count:7,}  {ida}")

    print("\nSample usable location descriptions:")
    for item in examples:
        print("-" * 70)
        print(f"Project ID   : {item['project_id']}")
        print(f"State        : {item['state']}")
        print(f"Constituency : {item['constituency']}")
        print(f"IDA          : {item['ida']}")
        print(f"Signals      : {', '.join(item['signals'])}")
        print(f"Description  : {item['description']}")


if __name__ == "__main__":
    main()