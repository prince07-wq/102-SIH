"""
scripts/detect_duplicate_anomalies.py

Produces an explainable duplicate/similarity-risk score for every project
in data/processed/features.json, using EXACT normalized work_description
matching only (no fuzzy/edit-distance matching in V1).

A candidate group requires all of:
  - same normalized work_description (unusable/generic descriptions excluded)
  - same state_name
  - same constituency
  - same sanction_amount
  - same ida_name

For each project in a candidate group, the nearest sanction_date match to
any other group member determines the score tier.

IMPORTANT: these are repetition/duplicate-RISK signals requiring human
review. They are NOT confirmed duplicate projects and NOT fraud findings.
This script does not modify Cost V1, Delay V1, Expenditure V1, or feature
generation.
"""

import json
import os
import re
import sys
from collections import defaultdict, Counter
from datetime import date

FEATURES_PATH = os.path.join("data", "processed", "features.json")
OUTPUT_PATH = os.path.join("data", "processed", "duplicate_anomalies.json")

FLAG_THRESHOLD = 50
MAX_SIMILAR_PROJECTS = 10

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


def normalize_description(text):
    """Lowercases, strips punctuation, and collapses whitespace. No fuzzy logic."""
    if is_missing(text) or not isinstance(text, str):
        return None
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else None


def is_generic(normalized):
    """Flags empty/placeholder/too-short descriptions as unusable for duplicate matching."""
    if normalized is None:
        return True
    if normalized in GENERIC_DESCRIPTIONS:
        return True
    if len(normalized) < MIN_USABLE_DESCRIPTION_LENGTH:
        return True
    return False


def safe_number(value):
    """Safely parses a numeric value that may already be a number or a string. Returns float or None."""
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
    """Parses an ISO 'YYYY-MM-DD' string into a date object. Returns None if missing/invalid."""
    if is_missing(value) or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def build_matching_evidence(project):
    """
    Returns the matching-key tuple for a project, or None if the project is
    ineligible for duplicate-candidate matching (unusable description or any
    required field missing). Missing fields are never treated as "matching".
    """
    normalized_description = project["_normalized_description"]
    if is_generic(normalized_description):
        return None, "unusable_description"

    state_name = project.get("state_name")
    constituency = project.get("constituency")
    sanction_amount = safe_number(project.get("sanction_amount"))
    ida_name = project.get("ida_name")

    if is_missing(state_name) or is_missing(constituency) or sanction_amount is None or is_missing(ida_name):
        return None, "missing_required_field"

    key = (normalized_description, state_name, constituency, round(sanction_amount, 2), ida_name)
    return key, "eligible"


def build_candidate_groups(projects):
    """
    Groups projects by exact matching evidence, keeping only groups with 2+
    members. Returns (groups_by_key, eligibility_status_per_project_id).
    """
    buckets = defaultdict(list)
    statuses = {}

    for project in projects:
        key, status = build_matching_evidence(project)
        statuses[id(project)] = status
        if key is not None:
            buckets[key].append(project)

    candidate_groups = {key: members for key, members in buckets.items() if len(members) >= 2}
    return candidate_groups, statuses


def find_nearest_match(project, group_members):
    """
    Finds the minimum absolute sanction_date difference (in days) between
    `project` and any other member of its group. Returns None if the
    project's own date, or every other member's date, is unavailable.
    """
    own_date = safe_iso_date(project.get("sanction_date"))
    if own_date is None:
        return None

    min_diff = None
    for other in group_members:
        if other is project:
            continue
        other_date = safe_iso_date(other.get("sanction_date"))
        if other_date is None:
            continue
        diff = abs((own_date - other_date).days)
        if min_diff is None or diff < min_diff:
            min_diff = diff

    return min_diff


def score_for_nearest_match(min_diff_days):
    """
    Converts the nearest-match date difference into a score tier.
    None means a candidate group exists but date proximity could not be
    determined (missing dates) -- treated the same as "over 30 days" since
    we cannot claim closer proximity without evidence.
    """
    if min_diff_days is None:
        return 30.0, "date_unavailable"
    if min_diff_days == 0:
        return 80.0, "same_date"
    if min_diff_days <= 7:
        return 70.0, "within_7_days"
    if min_diff_days <= 30:
        return 50.0, "within_30_days"
    return 30.0, "over_30_days"


def build_similar_projects(project, group_members):
    """Builds the bounded, sorted list of closest-matching projects for output."""
    own_date = safe_iso_date(project.get("sanction_date"))
    entries = []

    for other in group_members:
        if other is project:
            continue
        other_date = safe_iso_date(other.get("sanction_date"))
        if own_date is not None and other_date is not None:
            date_difference_days = abs((own_date - other_date).days)
        else:
            date_difference_days = None

        entries.append({
            "project_id": other.get("project_id"),
            "sanction_amount": other.get("sanction_amount"),
            "sanction_date": other.get("sanction_date"),
            "date_difference_days": date_difference_days,
            "work_description": other.get("work_description"),
        })

    entries.sort(
        key=lambda e: (
            e["date_difference_days"] if e["date_difference_days"] is not None else float("inf"),
            str(e["project_id"]),
        )
    )
    return entries[:MAX_SIMILAR_PROJECTS]


def build_reason(status, group_size, min_diff_days, tier):
    """Builds a human-readable, neutral explanation that avoids fraud/duplicate-confirmation language."""
    if status == "unusable_description":
        return (
            "This project's work description is empty, generic, or a placeholder value, "
            "so duplicate-candidate matching could not be applied."
        )

    if status == "missing_required_field":
        return (
            "One or more fields required for duplicate-candidate matching (state, constituency, "
            "sanction amount, or implementing authority) are missing, so matching could not be applied."
        )

    if status == "no_group":
        return (
            "No other project shares an identical description, state, constituency, sanction amount, "
            "and implementing authority combination; no duplicate-candidate group applies."
        )

    other_count = group_size - 1
    base = (
        f"This project shares an identical work description, state, constituency, sanction amount, "
        f"and implementing authority with {other_count} other project(s)."
    )

    if tier == "date_unavailable":
        proximity = " The sanction date is missing or invalid, so temporal proximity could not be confirmed."
    elif tier == "same_date":
        proximity = " The nearest matching project has the same sanction date."
    elif tier == "within_7_days":
        proximity = f" The nearest matching project's sanction date is {min_diff_days} day(s) away."
    elif tier == "within_30_days":
        proximity = f" The nearest matching project's sanction date is {min_diff_days} day(s) away."
    else:
        proximity = f" The nearest matching project's sanction date is {min_diff_days} day(s) away."

    disclaimer = (
        " This is a candidate repetition pattern requiring review, not a confirmed duplicate or fraud finding."
    )
    return base + proximity + disclaimer


def evaluate_project(project, candidate_groups, statuses):
    """Computes the full duplicate-anomaly result dict for a single project."""
    key, status = build_matching_evidence(project)
    group_members = candidate_groups.get(key) if key is not None else None

    if group_members is None or len(group_members) < 2:
        # Eligible on its own fields, but no other project matches -> no_group.
        final_status = status if status != "eligible" else "no_group"
        result = {
            "project_id": project.get("project_id"),
            "score": 0.0,
            "flagged": False,
            "reason": build_reason(final_status, 0, None, None),
            "normalized_description": project["_normalized_description"],
            "candidate_group_size": 0,
            "nearest_date_difference_days": None,
            "matching_evidence": None,
            "similar_projects": [],
        }
        return result, final_status, None

    min_diff = find_nearest_match(project, group_members)
    score, tier = score_for_nearest_match(min_diff)
    flagged = score >= FLAG_THRESHOLD

    similar_projects = build_similar_projects(project, group_members)

    matching_evidence = {
        "normalized_description": key[0],
        "state_name": key[1],
        "constituency": key[2],
        "sanction_amount": key[3],
        "ida_name": key[4],
    }

    result = {
        "project_id": project.get("project_id"),
        "score": score,
        "flagged": flagged,
        "reason": build_reason("candidate", len(group_members), min_diff, tier),
        "normalized_description": project["_normalized_description"],
        "candidate_group_size": len(group_members),
        "nearest_date_difference_days": min_diff,
        "matching_evidence": matching_evidence,
        "similar_projects": similar_projects,
    }
    return result, "candidate", tier


def bucket_score(score):
    """Returns which display bucket a score falls into."""
    if score < 20:
        return "0-19"
    if score < 50:
        return "20-49"
    if score < 80:
        return "50-79"
    return "80-100"


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(total_projects, status_counts, tier_counts, results, output_path):
    flagged_count = sum(1 for r in results if r["flagged"])
    score_buckets = Counter(bucket_score(r["score"]) for r in results)

    print("\n--- Duplicate/Similarity Anomaly Detection Summary ---")
    print(f"Total projects: {total_projects}")
    print(f"Unusable descriptions: {status_counts.get('unusable_description', 0)}")
    print(
        "Projects with no candidate group: "
        f"{status_counts.get('no_group', 0) + status_counts.get('missing_required_field', 0)}"
    )
    print(f"Candidate projects (in a matching group of 2+): {status_counts.get('candidate', 0)}")

    print(f"\nSame-day projects: {tier_counts.get('same_date', 0)}")
    print(f"Within 7 days: {tier_counts.get('within_7_days', 0)}")
    print(f"Within 30 days: {tier_counts.get('within_30_days', 0)}")
    print(f"Over 30 days: {tier_counts.get('over_30_days', 0)}")
    print(f"Date unavailable (candidate group, proximity unknown): {tier_counts.get('date_unavailable', 0)}")

    print(f"\nFlagged count (score >= {FLAG_THRESHOLD}): {flagged_count}")
    flagged_percentage = (flagged_count / total_projects * 100) if total_projects else 0.0
    print(f"Flagged percentage: {flagged_percentage:.2f}%")

    print("\nScore distribution:")
    for bucket in ["0-19", "20-49", "50-79", "80-100"]:
        print(f"  {bucket}: {score_buckets.get(bucket, 0)}")

    top_10 = sorted(results, key=lambda r: r["score"], reverse=True)[:10]
    print("\nTop 10 highest-risk examples:")
    for r in top_10:
        print(
            f"  {r['project_id']}: score={r['score']} group_size={r['candidate_group_size']} "
            f"nearest_diff_days={r['nearest_date_difference_days']}"
        )

    print(f"\nOutput path: {output_path}")


def main():
    try:
        projects = load_features(FEATURES_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load features data: {e}")
        sys.exit(1)

    for project in projects:
        project["_normalized_description"] = normalize_description(project.get("work_description"))

    candidate_groups, _ = build_candidate_groups(projects)

    results = []
    status_counts = Counter()
    tier_counts = Counter()

    for project in projects:
        result, status, tier = evaluate_project(project, candidate_groups, {})
        results.append(result)
        status_counts[status] += 1
        if tier is not None:
            tier_counts[tier] += 1

    try:
        save_json(results, OUTPUT_PATH)
    except OSError as e:
        print(f"ERROR: Failed to save output: {e}")
        sys.exit(1)

    print("SUCCESS: Duplicate/similarity anomaly detection complete.")
    print_summary(len(projects), status_counts, tier_counts, results, OUTPUT_PATH)


if __name__ == "__main__":
    main()
    