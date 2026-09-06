"""
scripts/build_combined_risk.py

Joins the four frozen anomaly detector outputs by project_id and produces
a single combined risk score per project.

Inputs (read-only, not modified):
  data/processed/cost_anomalies.json
  data/processed/delay_anomalies.json
  data/processed/expenditure_anomalies.json
  data/processed/duplicate_anomalies.json

Output:
  data/processed/combined_risk.json

Formula (confirmed):
  overall_before_bonus = max(cost_score, delay_score, expenditure_score, duplicate_score)
  flag_count            = number of the 4 component scores that are >= 50
  bonus                 = 0 (0-1 flags), +10 (2 flags), +15 (3 flags), +20 (4 flags)
  overall_score         = min(100, overall_before_bonus + bonus)

Risk levels:
  0-19 LOW, 20-49 MODERATE, 50-79 HIGH, 80-100 CRITICAL

This script does not modify any of the 4 detectors or their output files.
"""

import json
import os
import sys
from collections import Counter

COST_PATH = os.path.join("data", "processed", "cost_anomalies.json")
DELAY_PATH = os.path.join("data", "processed", "delay_anomalies.json")
EXPENDITURE_PATH = os.path.join("data", "processed", "expenditure_anomalies.json")
DUPLICATE_PATH = os.path.join("data", "processed", "duplicate_anomalies.json")
OUTPUT_PATH = os.path.join("data", "processed", "combined_risk.json")

FLAG_THRESHOLD = 50

BONUS_BY_FLAG_COUNT = {0: 0, 1: 0, 2: 10, 3: 15, 4: 20}


def load_json_list(filepath):
    """Loads a JSON file and validates that its top-level structure is a list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {filepath}, got {type(data).__name__}")
    return data


def extract_component(record, nested_key):
    """Extracts {score, flagged, reason} from a detector record (nested or flat)."""
    source = record.get(nested_key, {}) if nested_key is not None else record
    return {
        "score": source.get("score"),
        "flagged": source.get("flagged"),
        "reason": source.get("reason"),
    }


def build_index(records, nested_key):
    """Builds project_id -> extracted component dict. Reports duplicate/missing IDs."""
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
        index[project_id] = extract_component(record, nested_key)

    return index, duplicate_count, missing_count


def build_similar_projects_index(duplicate_records):
    """Builds project_id -> similar_projects list from the duplicate detector output."""
    index = {}
    for record in duplicate_records:
        project_id = record.get("project_id")
        if project_id is None:
            continue
        index[project_id] = record.get("similar_projects", [])
    return index


def risk_level_for(score):
    """Maps a combined score to its risk level label."""
    if score < 20:
        return "LOW"
    if score < 50:
        return "MODERATE"
    if score < 80:
        return "HIGH"
    return "CRITICAL"


def compute_combined_result(project_id, cost, delay, expenditure, duplicate, similar_projects):
    """Computes overall_score, flag_count, and risk_level for one project."""
    scores = {
        "cost": cost["score"] or 0,
        "delay": delay["score"] or 0,
        "expenditure": expenditure["score"] or 0,
        "duplicate": duplicate["score"] or 0,
    }

    overall_before_bonus = max(scores.values())
    flag_count = sum(1 for value in scores.values() if value >= FLAG_THRESHOLD)
    bonus = BONUS_BY_FLAG_COUNT.get(flag_count, 0)
    overall_score = round(min(100, overall_before_bonus + bonus), 2)

    return {
        "project_id": project_id,
        "overall_score": overall_score,
        "risk_level": risk_level_for(overall_score),
        "flag_count": flag_count,
        "cost": cost,
        "delay": delay,
        "expenditure": expenditure,
        "duplicate": duplicate,
        "similar_projects": similar_projects,
    }


def report_id_validation(raw_counts, id_sets):
    """Prints basic record/ID hygiene before joining."""
    print("=== Record / ID Validation ===")
    for name, (total, duplicate_count, missing_count) in raw_counts.items():
        print(f"  {name}: {total} records, {duplicate_count} duplicate project_id(s), "
              f"{missing_count} missing project_id")

    all_ids = set.union(*id_sets.values())
    common_ids = set.intersection(*id_sets.values())
    print(f"\n  Union of all project_ids across files: {len(all_ids)}")
    print(f"  Intersection (present in all 4 files): {len(common_ids)}")

    for name, id_set in id_sets.items():
        missing_from_this = all_ids - id_set
        if missing_from_this:
            print(f"  project_ids missing from {name}: {len(missing_from_this)}")

    return common_ids


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(results, output_path):
    total = len(results)
    print("\n--- Combined Risk Summary ---")
    print(f"Projects scored: {total}")

    level_counts = Counter(r["risk_level"] for r in results)
    print("\nRisk level distribution:")
    for level in ["LOW", "MODERATE", "HIGH", "CRITICAL"]:
        count = level_counts.get(level, 0)
        pct = (count / total * 100) if total else 0.0
        print(f"  {level}: {count} ({pct:.2f}%)")

    flag_count_counts = Counter(r["flag_count"] for r in results)
    print("\nFlag-count distribution:")
    for n in range(0, 5):
        print(f"  {n} detector(s) flagged: {flag_count_counts.get(n, 0)}")

    top_10 = sorted(results, key=lambda r: (r["overall_score"], r["flag_count"]), reverse=True)[:10]
    print("\nTop 10 highest combined-risk projects:")
    for r in top_10:
        print(
            f"  {r['project_id']}: overall_score={r['overall_score']} risk_level={r['risk_level']} "
            f"flag_count={r['flag_count']} "
            f"(cost={r['cost']['score']}, delay={r['delay']['score']}, "
            f"expenditure={r['expenditure']['score']}, duplicate={r['duplicate']['score']})"
        )

    print(f"\nOutput path: {output_path}")


def main():
    try:
        cost_records = load_json_list(COST_PATH)
        delay_records = load_json_list(DELAY_PATH)
        expenditure_records = load_json_list(EXPENDITURE_PATH)
        duplicate_records = load_json_list(DUPLICATE_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load detector output: {e}")
        sys.exit(1)

    cost_index, cost_dup, cost_miss = build_index(cost_records, "cost")
    delay_index, delay_dup, delay_miss = build_index(delay_records, "delay")
    expenditure_index, exp_dup, exp_miss = build_index(expenditure_records, "expenditure")
    duplicate_index, dupdet_dup, dupdet_miss = build_index(duplicate_records, None)
    similar_projects_index = build_similar_projects_index(duplicate_records)

    raw_counts = {
        "cost": (len(cost_records), cost_dup, cost_miss),
        "delay": (len(delay_records), delay_dup, delay_miss),
        "expenditure": (len(expenditure_records), exp_dup, exp_miss),
        "duplicate": (len(duplicate_records), dupdet_dup, dupdet_miss),
    }
    id_sets = {
        "cost": set(cost_index.keys()),
        "delay": set(delay_index.keys()),
        "expenditure": set(expenditure_index.keys()),
        "duplicate": set(duplicate_index.keys()),
    }

    common_ids = report_id_validation(raw_counts, id_sets)

    results = []
    for record in cost_records:
        project_id = record.get("project_id")
        if project_id not in common_ids:
            continue
        result = compute_combined_result(
            project_id,
            cost_index[project_id],
            delay_index[project_id],
            expenditure_index[project_id],
            duplicate_index[project_id],
            similar_projects_index.get(project_id, []),
        )
        results.append(result)

    try:
        save_json(results, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    print("\nSUCCESS: Combined risk build complete.")
    print_summary(results, OUTPUT_PATH)


if __name__ == "__main__":
    main()
    