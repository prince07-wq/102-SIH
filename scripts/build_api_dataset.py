"""
scripts/build_api_dataset.py

Builds one API-ready record per project by joining project metadata and
expenditure aggregates with the frozen Combined Risk V1 output.

Inputs (read-only, not modified):
  data/processed/projects.json
  data/processed/combined_risk.json

Output:
  data/processed/api_projects.json
"""

import json
import math
import os
import sys

PROJECTS_PATH = os.path.join("data", "processed", "projects.json")
COMBINED_RISK_PATH = os.path.join("data", "processed", "combined_risk.json")
OUTPUT_PATH = os.path.join("data", "processed", "api_projects.json")

RISK_FIELDS = [
    "overall_score",
    "risk_level",
    "flag_count",
    "cost",
    "delay",
    "expenditure",
    "duplicate",
    "similar_projects",
]

COMPONENT_FIELDS = ["score", "flagged", "reason"]
COMPONENT_NAMES = ["cost", "delay", "expenditure", "duplicate"]

EXPLANATION_FIELDS = [
    "base_score",
    "strongest_detector",
    "multi_signal_bonus",
    "score_capped",
]

BONUS_BY_FLAG_COUNT = {0: 0, 1: 0, 2: 10, 3: 15, 4: 20}

PROJECT_NUMERIC_FIELDS = [
    "sanction_amount",
    "expenditure_record_count",
    "total_disbursed",
    "unique_vendor_count",
]


def load_json_list(filepath):
    """Loads a JSON file and validates that its top-level structure is a list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {filepath}, got {type(data).__name__}")

    return data


def is_missing(value):
    """Treats None or a blank string as missing."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def is_valid_number(value):
    """Returns True for a finite int or float, excluding booleans."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_project_record(record, position):
    """Validates important project metadata and expenditure assumptions."""
    if not isinstance(record, dict):
        raise ValueError(
            f"Project record {position} must be an object, got {type(record).__name__}"
        )

    for field in PROJECT_NUMERIC_FIELDS:
        if not is_valid_number(record.get(field)):
            raise ValueError(
                f"Project record {position} has a missing or malformed numeric field: {field}"
            )

    if not isinstance(record.get("has_expenditure"), bool):
        raise ValueError(
            f"Project record {position} has a missing or malformed boolean field: has_expenditure"
        )

    for field in ["vendors", "work_ids"]:
        if not isinstance(record.get(field), list):
            raise ValueError(
                f"Project record {position} has a missing or malformed list field: {field}"
            )

    conflicting_fields = [
        field for field in RISK_FIELDS + EXPLANATION_FIELDS if field in record
    ]
    if conflicting_fields:
        raise ValueError(
            f"Project record {position} already contains risk field(s): "
            f"{', '.join(conflicting_fields)}"
        )


def validate_risk_component(component, component_name, position):
    """Validates one explainable risk component."""
    if not isinstance(component, dict):
        raise ValueError(
            f"Combined risk record {position} has a malformed {component_name} component"
        )

    missing_fields = [field for field in COMPONENT_FIELDS if field not in component]
    if missing_fields:
        raise ValueError(
            f"Combined risk record {position} {component_name} component is missing field(s): "
            f"{', '.join(missing_fields)}"
        )

    if not is_valid_number(component.get("score")):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed "
            f"{component_name}.score"
        )
    if not isinstance(component.get("flagged"), bool):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed "
            f"{component_name}.flagged"
        )
    if not isinstance(component.get("reason"), str) or is_missing(component.get("reason")):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed "
            f"{component_name}.reason"
        )


def validate_risk_record(record, position):
    """Validates the Combined Risk V1 fields required by the API dataset."""
    if not isinstance(record, dict):
        raise ValueError(
            f"Combined risk record {position} must be an object, got {type(record).__name__}"
        )

    missing_fields = [field for field in RISK_FIELDS if field not in record]
    if missing_fields:
        raise ValueError(
            f"Combined risk record {position} is missing field(s): {', '.join(missing_fields)}"
        )

    if not is_valid_number(record.get("overall_score")):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed overall_score"
        )
    if not isinstance(record.get("risk_level"), str) or is_missing(record.get("risk_level")):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed risk_level"
        )
    if not isinstance(record.get("flag_count"), int) or isinstance(
        record.get("flag_count"), bool
    ):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed flag_count"
        )
    if record.get("flag_count") not in BONUS_BY_FLAG_COUNT:
        raise ValueError(
            f"Combined risk record {position} has flag_count outside 0-4"
        )
    if not isinstance(record.get("similar_projects"), list):
        raise ValueError(
            f"Combined risk record {position} has a missing or malformed similar_projects"
        )

    for component_name in COMPONENT_NAMES:
        validate_risk_component(record.get(component_name), component_name, position)


def build_index(records, record_name, validator):
    """Builds a project_id lookup and counts missing and duplicate IDs."""
    index = {}
    missing_id_count = 0
    duplicate_id_count = 0

    for position, record in enumerate(records, start=1):
        validator(record, position)
        project_id = record.get("project_id")

        if is_missing(project_id) or isinstance(project_id, (bool, list, dict)):
            missing_id_count += 1
            continue
        if project_id in index:
            duplicate_id_count += 1
            continue

        index[project_id] = record

    return index, {
        "record_name": record_name,
        "record_count": len(records),
        "missing_id_count": missing_id_count,
        "duplicate_id_count": duplicate_id_count,
    }


def validate_join(project_index, risk_index, project_stats, risk_stats):
    """Validates ID hygiene and requires a complete one-to-one join."""
    projects_without_risk = set(project_index) - set(risk_index)
    risks_without_project = set(risk_index) - set(project_index)

    join_stats = {
        "projects_without_risk": len(projects_without_risk),
        "risks_without_project": len(risks_without_project),
    }

    has_id_problems = any(
        [
            project_stats["missing_id_count"],
            project_stats["duplicate_id_count"],
            risk_stats["missing_id_count"],
            risk_stats["duplicate_id_count"],
        ]
    )

    if has_id_problems or projects_without_risk or risks_without_project:
        raise ValueError(
            "Join validation failed: "
            f"projects missing/invalid IDs={project_stats['missing_id_count']}, "
            f"duplicate project IDs={project_stats['duplicate_id_count']}, "
            f"combined risk missing/invalid IDs={risk_stats['missing_id_count']}, "
            f"duplicate combined risk IDs={risk_stats['duplicate_id_count']}, "
            f"projects without risk={join_stats['projects_without_risk']}, "
            f"risk records without project={join_stats['risks_without_project']}"
        )

    return join_stats


def build_api_records(projects, risk_index):
    """Joins project and combined-risk fields while preserving project order."""
    api_records = []

    for project in projects:
        project_id = project["project_id"]
        risk = risk_index[project_id]
        record = dict(project)
        for field in RISK_FIELDS:
            record[field] = risk[field]
        component_scores = {
            component_name: float(risk[component_name]["score"])
            for component_name in COMPONENT_NAMES
        }
        strongest_detector = max(component_scores, key=component_scores.get)
        base_score = component_scores[strongest_detector]
        multi_signal_bonus = BONUS_BY_FLAG_COUNT[risk["flag_count"]]
        record["base_score"] = base_score
        record["strongest_detector"] = strongest_detector
        record["multi_signal_bonus"] = multi_signal_bonus
        record["score_capped"] = base_score + multi_signal_bonus > 100
        api_records.append(record)

    return api_records


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(api_records, project_stats, risk_stats, join_stats, output_path):
    """Prints a concise build and join-validation summary."""
    print("\n--- API Dataset Build Summary ---")
    print(f"Projects processed: {len(api_records)}")
    print(f"Project records with missing/invalid IDs: {project_stats['missing_id_count']}")
    print(f"Duplicate project IDs: {project_stats['duplicate_id_count']}")
    print(f"Combined risk records with missing/invalid IDs: {risk_stats['missing_id_count']}")
    print(f"Duplicate combined risk IDs: {risk_stats['duplicate_id_count']}")
    print(f"Projects without combined risk: {join_stats['projects_without_risk']}")
    print(f"Combined risk records without projects: {join_stats['risks_without_project']}")
    print(f"Output path: {output_path}")


def main():
    try:
        projects = load_json_list(PROJECTS_PATH)
        risk_records = load_json_list(COMBINED_RISK_PATH)

        project_index, project_stats = build_index(
            projects, "project", validate_project_record
        )
        risk_index, risk_stats = build_index(
            risk_records, "combined risk", validate_risk_record
        )
        join_stats = validate_join(
            project_index, risk_index, project_stats, risk_stats
        )
        api_records = build_api_records(projects, risk_index)
        save_json(api_records, OUTPUT_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to build API dataset: {e}")
        sys.exit(1)

    print("SUCCESS: API dataset build complete.")
    print_summary(api_records, project_stats, risk_stats, join_stats, OUTPUT_PATH)


if __name__ == "__main__":
    main()
