"""
ml/validate_behavioral_iforest.py

Runs final semantic and stability diagnostics for the experimental
behavioral-only Isolation Forest architecture. It does not change the frozen
rule engine, train a production model, or create ml_anomalies.json.
"""

import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.ensemble import IsolationForest

from run_isolation_forest_experiment import (
    COHORT_B,
    MODEL_PARAMETERS,
    build_matrix,
    percentile_anomaly_scores,
)


FEATURES_PATH = os.path.join("data", "processed", "features.json")
PROJECTS_PATH = os.path.join("data", "processed", "projects.json")
PHASE3_PATH = os.path.join(
    "data", "processed", "experiments", "isolation_forest_phase3.json"
)
OUTPUT_PATH = os.path.join(
    "data", "processed", "experiments", "behavioral_iforest_phase5.json"
)

BASELINE_RANDOM_STATE = 42
STABILITY_RANDOM_STATES = (7, 21, 99)
PERCENTILE_THRESHOLDS = (97.0, 97.5, 98.0, 99.0)
TOP_COUNTS = (100, 500)
VENDOR_IDENTIFICATION_STAGE = "Vendor Identification"
MISSING_STAGE = "__MISSING__"


def load_json(filepath, expected_type):
    """Loads JSON and validates its top-level type."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, expected_type):
        raise ValueError(
            f"Expected {expected_type.__name__} in {filepath}, "
            f"got {type(data).__name__}"
        )
    return data


def index_unique(records, label):
    """Indexes records by unique integer project_id."""
    indexed = {}
    for record in records:
        project_id = record.get("project_id")
        if isinstance(project_id, bool) or not isinstance(project_id, int):
            raise ValueError(f"Invalid project_id in {label}: {project_id!r}")
        if project_id in indexed:
            raise ValueError(f"Duplicate project_id {project_id} in {label}")
        indexed[project_id] = record
    return indexed


def linear_percentile(values, percentile):
    """Calculates a linearly interpolated percentile."""
    return float(np.percentile(values, percentile, method="linear"))


def distribution_summary(values):
    """Returns descriptive distribution statistics."""
    values = np.asarray(values, dtype=float)
    if not len(values):
        return None
    return {
        "min": float(np.min(values)),
        "median": linear_percentile(values, 50),
        "p95": linear_percentile(values, 95),
        "p99": linear_percentile(values, 99),
        "max": float(np.max(values)),
    }


def tukey_threshold(values):
    """Calculates the upper Tukey fence for anomaly values."""
    q1 = linear_percentile(values, 25)
    q3 = linear_percentile(values, 75)
    iqr = q3 - q1
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "raw_anomaly_value_threshold": q3 + 1.5 * iqr,
    }


def overlap_summary(left_ids, right_ids):
    """Summarizes set overlap without assuming equal set sizes."""
    left_ids = set(left_ids)
    right_ids = set(right_ids)
    intersection = len(left_ids & right_ids)
    union = len(left_ids | right_ids)
    return {
        "left_count": len(left_ids),
        "right_count": len(right_ids),
        "overlap_count": intersection,
        "left_recall": intersection / len(left_ids) if left_ids else None,
        "right_recall": intersection / len(right_ids) if right_ids else None,
        "jaccard": intersection / union if union else None,
    }


def rank_overlap(project_ids, baseline_values, comparison_values, count):
    """Calculates top-N overlap for two aligned score arrays."""
    baseline_order = np.argsort(-baseline_values, kind="mergesort")[:count]
    comparison_order = np.argsort(-comparison_values, kind="mergesort")[:count]
    baseline_ids = {project_ids[index] for index in baseline_order}
    comparison_ids = {project_ids[index] for index in comparison_order}
    return overlap_summary(baseline_ids, comparison_ids)


def spearman_from_percentiles(left, right):
    """Calculates Spearman correlation from empirical midrank percentiles."""
    left_ranks = percentile_anomaly_scores(left)
    right_ranks = percentile_anomaly_scores(right)
    return float(np.corrcoef(left_ranks, right_ranks)[0, 1])


def stage_name(record):
    """Returns a stable stage label."""
    value = record.get("work_stage")
    if value is None or not str(value).strip():
        return MISSING_STAGE
    return str(value).strip()


def group_diagnostics(records, anomaly_flags, ml_scores):
    """Builds the requested distributions for a project group."""
    count = len(records)
    anomaly_count = int(np.sum(anomaly_flags))
    return {
        "project_count": count,
        "ml_anomaly_count": anomaly_count,
        "ml_anomaly_rate": anomaly_count / count,
        "ml_score": {
            "median": linear_percentile(ml_scores, 50),
            "p95": linear_percentile(ml_scores, 95),
        },
        "expenditure_record_count": distribution_summary(
            [record["expenditure_record_count"] for record in records]
        ),
        "unique_vendor_count": distribution_summary(
            [record["unique_vendor_count"] for record in records]
        ),
        "disbursement_ratio": distribution_summary(
            [record["disbursement_ratio"] for record in records]
        ),
        "days_to_first_expenditure": distribution_summary(
            [record["days_to_first_expenditure"] for record in records]
        ),
    }


def fit_scores(records, random_state):
    """Fits the frozen cost-ablated preprocessing/model and returns scores."""
    matrix, details, feature_names = build_matrix(
        records, COHORT_B, include_cost_ratio=False
    )
    parameters = {**MODEL_PARAMETERS, "random_state": random_state}
    model = IsolationForest(**parameters)
    model.fit(matrix)
    raw_scores = model.score_samples(matrix)
    anomaly_values = -raw_scores
    percentile_scores = percentile_anomaly_scores(anomaly_values)
    return {
        "project_ids": np.asarray(
            [detail["project_id"] for detail in details], dtype=int
        ),
        "feature_names": feature_names,
        "raw_scores": raw_scores,
        "anomaly_values": anomaly_values,
        "percentile_scores": percentile_scores,
        "effective_max_samples": int(model.max_samples_),
    }


def analyze_stages(records, baseline):
    """Analyzes baseline ML behavior by existing work stage."""
    grouped_indexes = defaultdict(list)
    for index, record in enumerate(records):
        grouped_indexes[stage_name(record)].append(index)

    threshold = baseline["threshold"]
    report = {}
    for stage, indexes in sorted(grouped_indexes.items()):
        index_array = np.asarray(indexes, dtype=int)
        stage_records = [records[index] for index in indexes]
        anomaly_flags = (
            baseline["anomaly_values"][index_array] >= threshold
        )
        report[stage] = group_diagnostics(
            stage_records,
            anomaly_flags,
            baseline["percentile_scores"][index_array],
        )
    return report, grouped_indexes


def analyze_same_day(records, baseline):
    """Analyzes projects whose first expenditure is on sanction day."""
    indexes = np.asarray([
        index
        for index, record in enumerate(records)
        if record["days_to_first_expenditure"] == 0
    ], dtype=int)
    anomaly_flags = baseline["anomaly_values"][indexes] >= baseline["threshold"]
    same_day_records = [records[index] for index in indexes]
    stage_counts = Counter(stage_name(record) for record in same_day_records)
    return {
        "project_count": len(indexes),
        "project_rate": len(indexes) / len(records),
        "ml_anomaly_count": int(np.sum(anomaly_flags)),
        "ml_anomaly_rate_within_same_day": float(np.mean(anomaly_flags)),
        "share_of_all_ml_anomalies": (
            float(np.sum(anomaly_flags)) / baseline["anomaly_count"]
        ),
        "stage_distribution": dict(sorted(stage_counts.items())),
        "sanction_amount": distribution_summary(
            [record["sanction_amount"] for record in same_day_records]
        ),
        "disbursement_ratio": distribution_summary(
            [record["disbursement_ratio"] for record in same_day_records]
        ),
        "expenditure_record_count": distribution_summary(
            [record["expenditure_record_count"] for record in same_day_records]
        ),
        "unique_vendor_count": distribution_summary(
            [record["unique_vendor_count"] for record in same_day_records]
        ),
    }


def analyze_age_bands(records, baseline):
    """Calculates anomaly rates for the approved age bands."""
    bands = (
        ("0-30", 0, 30),
        ("31-90", 31, 90),
        ("91-180", 91, 180),
        ("181-365", 181, 365),
        ("366+", 366, math.inf),
    )
    report = {}
    for label, lower, upper in bands:
        indexes = np.asarray([
            index
            for index, record in enumerate(records)
            if lower <= record["days_since_sanction"] <= upper
        ], dtype=int)
        flags = baseline["anomaly_values"][indexes] >= baseline["threshold"]
        report[label] = {
            "project_count": len(indexes),
            "project_rate": len(indexes) / len(records),
            "ml_anomaly_count": int(np.sum(flags)),
            "ml_anomaly_rate": float(np.mean(flags)),
            "median_ml_score": linear_percentile(
                baseline["percentile_scores"][indexes], 50
            ),
            "p95_ml_score": linear_percentile(
                baseline["percentile_scores"][indexes], 95
            ),
        }
    return report


def analyze_vendor_semantics(records, projects):
    """Checks aggregate vendor counts against records and source vendor lists."""
    ratios = []
    patterns = Counter()
    equal_count = 0
    one_vendor = 0
    list_mismatches = 0
    projects_with_missing_vendor_id = 0
    projects_with_missing_vendor_name = 0

    for record in records:
        record_count = record["expenditure_record_count"]
        vendor_count = record["unique_vendor_count"]
        if vendor_count > record_count:
            raise ValueError(
                f"Project {record['project_id']} has more vendors than records"
            )
        ratios.append(vendor_count / record_count)
        patterns[(record_count, vendor_count)] += 1
        equal_count += vendor_count == record_count
        one_vendor += vendor_count == 1

        project_vendors = projects[record["project_id"]].get("vendors") or []
        if len(project_vendors) != vendor_count:
            list_mismatches += 1
        projects_with_missing_vendor_id += any(
            vendor.get("vendor_id") is None for vendor in project_vendors
        )
        projects_with_missing_vendor_name += any(
            vendor.get("vendor_name") is None for vendor in project_vendors
        )

    return {
        "definition_from_pipeline": (
            "Distinct expenditure-row vendor ID; when ID is missing, "
            "distinct vendor name is the fallback key"
        ),
        "vendor_to_record_ratio": distribution_summary(ratios),
        "vendor_equals_record_count": {
            "project_count": equal_count,
            "project_rate": equal_count / len(records),
        },
        "one_unique_vendor": {
            "project_count": one_vendor,
            "project_rate": one_vendor / len(records),
        },
        "vendor_count_greater_than_record_count": 0,
        "projects_where_vendor_list_length_differs_from_count": list_mismatches,
        "projects_with_any_missing_vendor_id": projects_with_missing_vendor_id,
        "projects_with_any_missing_vendor_name": projects_with_missing_vendor_name,
        "most_common_record_vendor_patterns": [
            {
                "expenditure_record_count": pattern[0],
                "unique_vendor_count": pattern[1],
                "project_count": count,
                "project_rate": count / len(records),
            }
            for pattern, count in patterns.most_common(15)
        ],
    }


def analyze_percentile_thresholds(baseline):
    """Compares requested percentile cutoffs with the frozen Tukey set."""
    tukey_ids = set(
        baseline["project_ids"][
            baseline["anomaly_values"] >= baseline["threshold"]
        ].tolist()
    )
    report = {}
    for threshold in PERCENTILE_THRESHOLDS:
        percentile_ids = set(
            baseline["project_ids"][
                baseline["percentile_scores"] >= threshold
            ].tolist()
        )
        report[str(threshold)] = {
            "project_count": len(percentile_ids),
            "project_rate": len(percentile_ids) / len(baseline["project_ids"]),
            "overlap_with_tukey": overlap_summary(tukey_ids, percentile_ids),
        }
    return report


def analyze_seed_stability(records, baseline):
    """Fits the requested alternate seeds and compares rankings/anomaly sets."""
    baseline_ids = baseline["project_ids"]
    baseline_anomaly_ids = set(
        baseline_ids[
            baseline["anomaly_values"] >= baseline["threshold"]
        ].tolist()
    )
    report = {}

    for random_state in STABILITY_RANDOM_STATES:
        alternate = fit_scores(records, random_state)
        if not np.array_equal(baseline_ids, alternate["project_ids"]):
            raise ValueError("Alternate seed changed project ordering")
        alternate_threshold = tukey_threshold(alternate["anomaly_values"])
        alternate_cutoff = alternate_threshold["raw_anomaly_value_threshold"]
        alternate_anomaly_ids = set(
            baseline_ids[
                alternate["anomaly_values"] >= alternate_cutoff
            ].tolist()
        )
        fixed_threshold_ids = set(
            baseline_ids[
                alternate["anomaly_values"] >= baseline["threshold"]
            ].tolist()
        )
        report[str(random_state)] = {
            "model_parameters": {
                **MODEL_PARAMETERS,
                "random_state": random_state,
            },
            "effective_max_samples": alternate["effective_max_samples"],
            "spearman_score_correlation_with_seed_42": spearman_from_percentiles(
                baseline["anomaly_values"], alternate["anomaly_values"]
            ),
            "top_overlap": {
                str(count): rank_overlap(
                    baseline_ids,
                    baseline["anomaly_values"],
                    alternate["anomaly_values"],
                    count,
                )
                for count in TOP_COUNTS
            },
            "seed_specific_tukey_threshold": alternate_threshold,
            "seed_specific_tukey_anomaly_overlap": overlap_summary(
                baseline_anomaly_ids, alternate_anomaly_ids
            ),
            "frozen_seed_42_threshold_anomaly_overlap": overlap_summary(
                baseline_anomaly_ids, fixed_threshold_ids
            ),
        }
    return report


def analyze_stage_counterfactuals(records, baseline, grouped_indexes):
    """Tests Vendor Identification exclusion and binary stage stratification."""
    vi_indexes = np.asarray(
        grouped_indexes.get(VENDOR_IDENTIFICATION_STAGE, []), dtype=int
    )
    vi_index_set = set(vi_indexes.tolist())
    non_vi_indexes = np.asarray([
        index for index in range(len(records)) if index not in vi_index_set
    ], dtype=int)

    report = {}
    stratified_anomaly_ids = set()
    for label, indexes in (
        ("VENDOR_IDENTIFICATION", vi_indexes),
        ("ALL_OTHER_STAGES", non_vi_indexes),
    ):
        subset_records = [records[index] for index in indexes]
        subset_fit = fit_scores(subset_records, BASELINE_RANDOM_STATE)
        subset_threshold = tukey_threshold(subset_fit["anomaly_values"])
        cutoff = subset_threshold["raw_anomaly_value_threshold"]
        subset_anomaly_ids = set(
            subset_fit["project_ids"][
                subset_fit["anomaly_values"] >= cutoff
            ].tolist()
        )
        baseline_subset_anomaly_ids = set(
            baseline["project_ids"][indexes][
                baseline["anomaly_values"][indexes] >= baseline["threshold"]
            ].tolist()
        )
        stratified_anomaly_ids.update(subset_anomaly_ids)
        report[label] = {
            "project_count": len(indexes),
            "refit_tukey_threshold": subset_threshold,
            "refit_anomaly_count": len(subset_anomaly_ids),
            "refit_anomaly_rate": len(subset_anomaly_ids) / len(indexes),
            "spearman_with_baseline_within_subset": spearman_from_percentiles(
                baseline["anomaly_values"][indexes],
                subset_fit["anomaly_values"],
            ),
            "top_overlap": {
                str(count): rank_overlap(
                    subset_fit["project_ids"],
                    baseline["anomaly_values"][indexes],
                    subset_fit["anomaly_values"],
                    min(count, len(indexes)),
                )
                for count in TOP_COUNTS
            },
            "anomaly_overlap": overlap_summary(
                baseline_subset_anomaly_ids, subset_anomaly_ids
            ),
        }

    baseline_anomaly_ids = set(
        baseline["project_ids"][
            baseline["anomaly_values"] >= baseline["threshold"]
        ].tolist()
    )
    report["COMBINED_BINARY_STRATIFICATION"] = {
        "anomaly_count": len(stratified_anomaly_ids),
        "anomaly_rate": len(stratified_anomaly_ids) / len(records),
        "overlap_with_baseline": overlap_summary(
            baseline_anomaly_ids, stratified_anomaly_ids
        ),
    }
    return report


def run_validation():
    """Runs all approved Phase 5 validation checks."""
    feature_records = load_json(FEATURES_PATH, list)
    project_records = load_json(PROJECTS_PATH, list)
    phase3 = load_json(PHASE3_PATH, dict)
    projects = index_unique(project_records, "projects")

    phase3_results = index_unique(phase3["project_results"], "Phase 3")
    records = [
        record
        for record in feature_records
        if record.get("has_expenditure") is True
    ]
    if len(records) != 55656:
        raise ValueError(f"Expected 55656 eligible projects, got {len(records)}")
    if set(projects) != {record["project_id"] for record in feature_records}:
        raise ValueError("Project IDs differ between projects and features")

    project_ids = np.asarray([record["project_id"] for record in records])
    baseline_raw_scores = np.asarray([
        phase3_results[project_id]["without_cost_ratio"][
            "raw_isolation_forest_score"
        ]
        for project_id in project_ids
    ])
    baseline_anomaly_values = -baseline_raw_scores
    baseline_percentiles = np.asarray([
        phase3_results[project_id]["without_cost_ratio"][
            "cohort_percentile_anomaly_score"
        ]
        for project_id in project_ids
    ])
    saved_threshold = phase3["cohorts"][COHORT_B]["without_cost_ratio"][
        "recommended_threshold"
    ]["raw_anomaly_value_threshold"]
    recalculated = tukey_threshold(baseline_anomaly_values)
    if not math.isclose(
        saved_threshold,
        recalculated["raw_anomaly_value_threshold"],
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise ValueError("Phase 3 baseline threshold failed verification")

    baseline = {
        "project_ids": project_ids,
        "raw_scores": baseline_raw_scores,
        "anomaly_values": baseline_anomaly_values,
        "percentile_scores": baseline_percentiles,
        "threshold": saved_threshold,
        "anomaly_count": int(np.sum(baseline_anomaly_values >= saved_threshold)),
    }
    stage_report, grouped_indexes = analyze_stages(records, baseline)
    vi_report = stage_report[VENDOR_IDENTIFICATION_STAGE]
    overall_anomaly_rate = baseline["anomaly_count"] / len(records)
    vi_report["share_of_eligible_projects"] = (
        vi_report["project_count"] / len(records)
    )
    vi_report["share_of_all_ml_anomalies"] = (
        vi_report["ml_anomaly_count"] / baseline["anomaly_count"]
    )
    vi_report["anomaly_rate_ratio_vs_all_eligible"] = (
        vi_report["ml_anomaly_rate"] / overall_anomaly_rate
    )

    return {
        "experiment": "Phase 5 behavioral-only Isolation Forest validation",
        "status": "EXPERIMENTAL",
        "architecture": "Cohort B without cost_vs_activity_median",
        "eligible_project_count": len(records),
        "baseline": {
            "random_state": BASELINE_RANDOM_STATE,
            "model_parameters": MODEL_PARAMETERS,
            "raw_anomaly_threshold": saved_threshold,
            "ml_anomaly_count": baseline["anomaly_count"],
            "ml_anomaly_rate": overall_anomaly_rate,
        },
        "work_stage_analysis": stage_report,
        "vendor_identification_analysis": vi_report,
        "same_day_expenditure_analysis": analyze_same_day(records, baseline),
        "project_age_band_analysis": analyze_age_bands(records, baseline),
        "vendor_semantics": analyze_vendor_semantics(records, projects),
        "threshold_stability": analyze_percentile_thresholds(baseline),
        "random_state_stability": analyze_seed_stability(records, baseline),
        "vendor_identification_counterfactuals": analyze_stage_counterfactuals(
            records, baseline, grouped_indexes
        ),
    }


def save_json(data, filepath):
    """Writes indented UTF-8 JSON, creating its output directory."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    try:
        report = run_validation()
        save_json(report, OUTPUT_PATH)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print("SUCCESS: Phase 5 behavioral-only validation complete.")
    print(f"Eligible projects: {report['eligible_project_count']}")
    print(f"ML anomalies: {report['baseline']['ml_anomaly_count']}")
    print(f"Output path: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
