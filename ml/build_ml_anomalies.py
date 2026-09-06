"""
ml/build_ml_anomalies.py

Builds the production ML V1 anomaly artifact from features.json and the frozen
Combined Risk V1 output. ML V1 applies only to projects with expenditure and
does not modify the existing explainable anomaly or combined-risk pipeline.
"""

import json
import math
import os
import sys
from collections import Counter

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
except ImportError as exc:
    print("ERROR: Missing ML dependencies. Install ml/requirements.txt.")
    raise SystemExit(1) from exc


FEATURES_PATH = os.path.join("data", "processed", "features.json")
COMBINED_RISK_PATH = os.path.join("data", "processed", "combined_risk.json")
OUTPUT_PATH = os.path.join("data", "processed", "ml_anomalies.json")

ML_ANOMALY_THRESHOLD = 0.593624456533016
RULE_ANOMALY_THRESHOLD = 50

MODEL_PARAMETERS = {
    "n_estimators": 300,
    "max_samples": "auto",
    "contamination": "auto",
    "max_features": 1.0,
    "bootstrap": False,
    "n_jobs": -1,
    "random_state": 42,
    "warm_start": False,
}

FEATURE_NAMES = [
    "log1p_sanction_amount",
    "days_since_sanction",
    "disbursement_ratio",
    "log1p_expenditure_record_count",
    "log1p_unique_vendor_count",
    "log1p_days_to_first_expenditure",
]

SOURCE_FEATURE_NAMES = [
    "sanction_amount",
    "days_since_sanction",
    "disbursement_ratio",
    "expenditure_record_count",
    "unique_vendor_count",
    "days_to_first_expenditure",
]

EXPECTED_TOTALS = {
    "total_projects": 78079,
    "ml_eligible": 55656,
    "ml_not_applicable": 22423,
    "ml_anomalies": 1799,
    "BOTH_HIGH": 1572,
    "ML_ONLY": 227,
    "RULE_ONLY": 12510,
    "NEITHER": 41347,
    "rule_anomalies_all_projects": 17774,
}


def load_json_list(filepath):
    """Loads and validates a JSON list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON list in {filepath}, got {type(data).__name__}"
        )
    return data


def index_unique(records, label):
    """Indexes records by a unique integer project_id."""
    indexed = {}
    for record in records:
        project_id = record.get("project_id")
        if isinstance(project_id, bool) or not isinstance(project_id, int):
            raise ValueError(f"Invalid project_id in {label}: {project_id!r}")
        if project_id in indexed:
            raise ValueError(f"Duplicate project_id {project_id} in {label}")
        indexed[project_id] = record
    return indexed


def require_number(record, field_name):
    """Returns a finite numeric field or raises a clear validation error."""
    value = record.get(field_name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"Project {record.get('project_id')} has invalid {field_name}: {value!r}"
        )
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(
            f"Project {record.get('project_id')} has non-finite {field_name}"
        )
    return value


def transform_eligible_project(record):
    """Applies the frozen Behavioral-only V1 preprocessing specification."""
    project_id = record["project_id"]
    values = {
        name: require_number(record, name)
        for name in SOURCE_FEATURE_NAMES
    }

    if values["sanction_amount"] < 0:
        raise ValueError(f"Project {project_id} has negative sanction_amount")
    if values["days_since_sanction"] < 0:
        raise ValueError(f"Project {project_id} has negative days_since_sanction")
    if not 0 <= values["disbursement_ratio"] <= 1:
        raise ValueError(
            f"Project {project_id} has disbursement_ratio outside [0, 1]"
        )
    for field_name in ("expenditure_record_count", "unique_vendor_count"):
        if values[field_name] < 1 or not values[field_name].is_integer():
            raise ValueError(
                f"Project {project_id} has invalid {field_name}: "
                f"{values[field_name]}"
            )
    if values["unique_vendor_count"] > values["expenditure_record_count"]:
        raise ValueError(
            f"Project {project_id} has more vendors than expenditure records"
        )
    if values["days_to_first_expenditure"] < 0:
        raise ValueError(
            f"Project {project_id} has negative days_to_first_expenditure"
        )

    transformed = [
        math.log1p(values["sanction_amount"]),
        values["days_since_sanction"],
        values["disbursement_ratio"],
        math.log1p(values["expenditure_record_count"]),
        math.log1p(values["unique_vendor_count"]),
        math.log1p(values["days_to_first_expenditure"]),
    ]
    return values, transformed


def percentile_anomaly_scores(anomaly_values):
    """Maps anomaly values to frozen empirical midrank percentiles from 0-100."""
    anomaly_values = np.asarray(anomaly_values, dtype=float)
    count = len(anomaly_values)
    if count < 2:
        raise ValueError("At least two eligible projects are required")

    order = np.argsort(anomaly_values, kind="mergesort")
    sorted_values = anomaly_values[order]
    percentiles = np.empty(count, dtype=float)
    start = 0

    while start < count:
        end = start + 1
        while end < count and sorted_values[end] == sorted_values[start]:
            end += 1
        zero_based_midrank = (start + end - 1) / 2.0
        percentile = 100.0 * zero_based_midrank / (count - 1)
        percentiles[order[start:end]] = percentile
        start = end

    return percentiles


def ml_anomaly_level(percentile_score):
    """Maps a percentile to a presentation band independent of the threshold.

    Mapping:
      0 to <90   -> BASELINE
      90 to <95  -> ELEVATED
      95 to <99  -> HIGH
      99 to 100  -> VERY_HIGH

    ML anomaly status is always determined separately from the frozen raw
    anomaly threshold, so a HIGH presentation level is not itself a flag.
    """
    if percentile_score >= 99:
        return "VERY_HIGH"
    if percentile_score >= 95:
        return "HIGH"
    if percentile_score >= 90:
        return "ELEVATED"
    return "BASELINE"


def ml_rule_agreement(ml_high, rule_high):
    """Returns the combined ML/rule comparison label for an eligible project."""
    if ml_high and rule_high:
        return "BOTH_HIGH"
    if ml_high:
        return "ML_ONLY"
    if rule_high:
        return "RULE_ONLY"
    return "NEITHER"


def fit_eligible_projects(eligible_records):
    """Fits frozen ML V1 and returns aligned score arrays and source values."""
    matrix_rows = []
    source_values = []
    for record in eligible_records:
        values, transformed = transform_eligible_project(record)
        source_values.append(values)
        matrix_rows.append(transformed)

    matrix = np.asarray(matrix_rows, dtype=float)
    if matrix.shape != (len(eligible_records), len(FEATURE_NAMES)):
        raise ValueError(f"Unexpected ML matrix shape: {matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("ML matrix contains non-finite values")

    model = IsolationForest(**MODEL_PARAMETERS)
    model.fit(matrix)
    raw_scores = model.score_samples(matrix)
    anomaly_values = -raw_scores
    percentile_scores = percentile_anomaly_scores(anomaly_values)
    return source_values, raw_scores, anomaly_values, percentile_scores


def build_eligible_record(record, values, raw_score, anomaly_value,
                          percentile_score, risk):
    """Builds one eligible project's production ML record."""
    ml_high = bool(anomaly_value >= ML_ANOMALY_THRESHOLD)
    rule_high = bool(risk["overall_score"] >= RULE_ANOMALY_THRESHOLD)
    return {
        "project_id": record["project_id"],
        "ml_eligible": True,
        "ml_raw_score": float(raw_score),
        "ml_anomaly_value": float(anomaly_value),
        "ml_anomaly_score": float(percentile_score),
        "ml_is_anomaly": ml_high,
        "ml_anomaly_level": ml_anomaly_level(percentile_score),
        "ml_rule_agreement": ml_rule_agreement(ml_high, rule_high),
        "project_age_days": int(values["days_since_sanction"]),
        "days_to_first_expenditure": int(values["days_to_first_expenditure"]),
        "expenditure_record_count": int(values["expenditure_record_count"]),
        "unique_vendor_count": int(values["unique_vendor_count"]),
        "disbursement_ratio": values["disbursement_ratio"],
        "work_stage": record.get("work_stage"),
    }


def build_not_applicable_record(record):
    """Builds one non-eligible project's explicit not-applicable record."""
    return {
        "project_id": record["project_id"],
        "ml_eligible": False,
        "ml_status": "ML_NOT_APPLICABLE",
        "ml_raw_score": None,
        "ml_anomaly_value": None,
        "ml_anomaly_score": None,
        "ml_is_anomaly": False,
        "ml_anomaly_level": None,
        "ml_rule_agreement": "ML_NOT_APPLICABLE",
    }


def validate_totals(output_records, risks):
    """Validates every frozen Phase 6 aggregate expectation."""
    counts = Counter()
    counts["total_projects"] = len(output_records)
    counts["ml_eligible"] = sum(
        record["ml_eligible"] for record in output_records
    )
    counts["ml_not_applicable"] = sum(
        not record["ml_eligible"] for record in output_records
    )
    counts["ml_anomalies"] = sum(
        record["ml_is_anomaly"] for record in output_records
    )
    counts["rule_anomalies_all_projects"] = sum(
        risk["overall_score"] >= RULE_ANOMALY_THRESHOLD
        for risk in risks.values()
    )
    for record in output_records:
        if record["ml_eligible"]:
            counts[record["ml_rule_agreement"]] += 1

    for name, expected in EXPECTED_TOTALS.items():
        actual = counts[name]
        if actual != expected:
            raise ValueError(
                f"Frozen total mismatch for {name}: expected {expected}, got {actual}"
            )
    return dict(counts)


def build_artifact(feature_records, risk_records):
    """Builds and validates the complete production artifact."""
    risks = index_unique(risk_records, "combined risk")
    feature_ids = [record.get("project_id") for record in feature_records]
    if len(set(feature_ids)) != len(feature_ids):
        raise ValueError("features.json contains duplicate project IDs")
    if set(feature_ids) != set(risks):
        raise ValueError("Project IDs differ between features and combined risk")

    eligible_records = []
    for record in feature_records:
        has_expenditure = record.get("has_expenditure")
        if not isinstance(has_expenditure, bool):
            raise ValueError(
                f"Project {record.get('project_id')} has invalid has_expenditure"
            )
        if has_expenditure:
            eligible_records.append(record)

    if len(eligible_records) != EXPECTED_TOTALS["ml_eligible"]:
        raise ValueError(
            f"Expected {EXPECTED_TOTALS['ml_eligible']} eligible projects, "
            f"got {len(eligible_records)}"
        )

    source_values, raw_scores, anomaly_values, percentile_scores = (
        fit_eligible_projects(eligible_records)
    )
    scored_by_id = {}
    for record, values, raw_score, anomaly_value, percentile_score in zip(
        eligible_records,
        source_values,
        raw_scores,
        anomaly_values,
        percentile_scores,
    ):
        project_id = record["project_id"]
        scored_by_id[project_id] = build_eligible_record(
            record,
            values,
            raw_score,
            anomaly_value,
            percentile_score,
            risks[project_id],
        )

    output_records = []
    for record in feature_records:
        project_id = record["project_id"]
        output_records.append(
            scored_by_id[project_id]
            if record["has_expenditure"]
            else build_not_applicable_record(record)
        )

    output_ids = [record["project_id"] for record in output_records]
    if output_ids != feature_ids:
        raise ValueError("Output project ordering differs from features.json")
    totals = validate_totals(output_records, risks)
    return output_records, totals


def save_json(data, filepath):
    """Writes indented UTF-8 JSON, creating its output directory."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    try:
        feature_records = load_json_list(FEATURES_PATH)
        risk_records = load_json_list(COMBINED_RISK_PATH)
        output_records, totals = build_artifact(feature_records, risk_records)
        save_json(output_records, OUTPUT_PATH)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print("SUCCESS: Production ML V1 artifact built.")
    print(f"Projects processed: {totals['total_projects']}")
    print(f"ML eligible: {totals['ml_eligible']}")
    print(f"ML anomalies: {totals['ml_anomalies']}")
    print(f"Threshold: {ML_ANOMALY_THRESHOLD}")
    print(f"Output path: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
