"""
ml/run_isolation_forest_experiment.py

Runs the first experimental Isolation Forest models for the two approved
expenditure cohorts. This is an offline experiment and does not modify the
existing rule-based anomaly pipeline or produce the final ML anomaly dataset.
"""

import argparse
import json
import math
import os
import sys

try:
    import numpy as np
    import sklearn
    from sklearn.ensemble import IsolationForest
except ImportError as exc:
    print("ERROR: Missing ML dependencies. Install ml/requirements.txt.")
    raise SystemExit(1) from exc


FEATURES_PATH = os.path.join("data", "processed", "features.json")
DEFAULT_OUTPUT_PATH = os.path.join(
    "data", "processed", "experiments", "isolation_forest_phase3.json"
)

RANDOM_STATE = 42
MODEL_PARAMETERS = {
    "n_estimators": 300,
    "max_samples": "auto",
    "contamination": "auto",
    "max_features": 1.0,
    "bootstrap": False,
    "n_jobs": -1,
    "random_state": RANDOM_STATE,
    "warm_start": False,
}

COHORT_A = "NO_EXPENDITURE"
COHORT_B = "HAS_EXPENDITURE"

# Frozen Phase 2 P99.5 caps from the approved cohort distributions.
COST_RATIO_CAPS = {
    COHORT_A: 12.331741,
    COHORT_B: 14.0074675,
}

FEATURE_NAMES = {
    COHORT_A: [
        "log1p_sanction_amount",
        "days_since_sanction",
        "clipped_log1p_cost_vs_activity_median",
    ],
    COHORT_B: [
        "log1p_sanction_amount",
        "days_since_sanction",
        "disbursement_ratio",
        "log1p_expenditure_record_count",
        "log1p_unique_vendor_count",
        "log1p_days_to_first_expenditure",
        "clipped_log1p_cost_vs_activity_median",
    ],
}

SOURCE_FEATURE_NAMES = {
    COHORT_A: [
        "sanction_amount",
        "days_since_sanction",
        "cost_vs_activity_median",
    ],
    COHORT_B: [
        "sanction_amount",
        "days_since_sanction",
        "disbursement_ratio",
        "expenditure_record_count",
        "unique_vendor_count",
        "days_to_first_expenditure",
        "cost_vs_activity_median",
    ],
}

PERCENTILE_THRESHOLDS = [95.0, 97.5, 99.0, 99.5, 99.9]
OVERLAP_COUNTS = [20, 50, 100]


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


def validate_project(record, cohort):
    """Validates the fields and value ranges required by one cohort."""
    project_id = record.get("project_id")
    if isinstance(project_id, bool) or not isinstance(project_id, int):
        raise ValueError(f"Invalid project_id: {project_id!r}")

    values = {
        name: require_number(record, name)
        for name in SOURCE_FEATURE_NAMES[cohort]
    }

    if values["sanction_amount"] < 0:
        raise ValueError(f"Project {project_id} has negative sanction_amount")
    if values["days_since_sanction"] < 0:
        raise ValueError(f"Project {project_id} has negative days_since_sanction")
    if values["cost_vs_activity_median"] < 0:
        raise ValueError(
            f"Project {project_id} has negative cost_vs_activity_median"
        )

    if cohort == COHORT_B:
        if not 0 <= values["disbursement_ratio"] <= 1:
            raise ValueError(
                f"Project {project_id} has disbursement_ratio outside [0, 1]"
            )
        for field_name in (
            "expenditure_record_count",
            "unique_vendor_count",
        ):
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

    return values


def transform_project(record, cohort, include_cost_ratio=True):
    """Applies the frozen V1 preprocessing specification to one project."""
    values = validate_project(record, cohort)
    transformed = {
        "log1p_sanction_amount": math.log1p(values["sanction_amount"]),
        "days_since_sanction": values["days_since_sanction"],
    }

    if cohort == COHORT_B:
        transformed.update({
            "disbursement_ratio": values["disbursement_ratio"],
            "log1p_expenditure_record_count": math.log1p(
                values["expenditure_record_count"]
            ),
            "log1p_unique_vendor_count": math.log1p(
                values["unique_vendor_count"]
            ),
            # Corrected Phase 2 transform: ln(days + 1), so zero maps to zero.
            "log1p_days_to_first_expenditure": math.log1p(
                values["days_to_first_expenditure"]
            ),
        })

    if include_cost_ratio:
        capped_ratio = min(
            values["cost_vs_activity_median"], COST_RATIO_CAPS[cohort]
        )
        transformed["clipped_log1p_cost_vs_activity_median"] = math.log1p(
            capped_ratio
        )

    feature_order = [
        name
        for name in FEATURE_NAMES[cohort]
        if include_cost_ratio
        or name != "clipped_log1p_cost_vs_activity_median"
    ]
    return values, transformed, feature_order


def split_cohorts(records):
    """Splits projects by the existing has_expenditure field."""
    cohorts = {COHORT_A: [], COHORT_B: []}
    seen_ids = set()

    for record in records:
        project_id = record.get("project_id")
        if project_id in seen_ids:
            raise ValueError(f"Duplicate project_id: {project_id}")
        seen_ids.add(project_id)

        has_expenditure = record.get("has_expenditure")
        if not isinstance(has_expenditure, bool):
            raise ValueError(
                f"Project {project_id} has non-boolean has_expenditure"
            )
        cohort = COHORT_B if has_expenditure else COHORT_A
        cohorts[cohort].append(record)

    return cohorts


def linear_percentile(values, percentile):
    """Calculates a linearly interpolated percentile."""
    return float(np.percentile(values, percentile, method="linear"))


def distribution_summary(values):
    """Returns the requested summary statistics for numeric values."""
    values = np.asarray(values, dtype=float)
    return {
        "min": float(np.min(values)),
        "median": linear_percentile(values, 50),
        "p95": linear_percentile(values, 95),
        "p99": linear_percentile(values, 99),
        "max": float(np.max(values)),
    }


def percentile_anomaly_scores(anomaly_values):
    """Maps anomaly values to 0-100 empirical midrank cohort percentiles."""
    anomaly_values = np.asarray(anomaly_values, dtype=float)
    count = len(anomaly_values)
    if count == 0:
        raise ValueError("Cannot normalize an empty score array")
    if count == 1:
        return np.array([50.0])

    order = np.argsort(anomaly_values, kind="mergesort")
    sorted_values = anomaly_values[order]
    percentiles = np.empty(count, dtype=float)
    start = 0

    while start < count:
        end = start + 1
        while end < count and sorted_values[end] == sorted_values[start]:
            end += 1
        midrank_zero_based = (start + end - 1) / 2.0
        percentile = 100.0 * midrank_zero_based / (count - 1)
        percentiles[order[start:end]] = percentile
        start = end

    return percentiles


def recommend_distribution_threshold(anomaly_values, percentile_scores):
    """Derives an exploratory threshold from the raw-score upper Tukey fence."""
    anomaly_values = np.asarray(anomaly_values, dtype=float)
    percentile_scores = np.asarray(percentile_scores, dtype=float)
    q1 = linear_percentile(anomaly_values, 25)
    q3 = linear_percentile(anomaly_values, 75)
    iqr = q3 - q1
    raw_threshold = q3 + 1.5 * iqr
    flagged = anomaly_values >= raw_threshold
    flagged_count = int(np.sum(flagged))
    normalized_threshold = (
        float(np.min(percentile_scores[flagged]))
        if flagged_count
        else 100.0
    )
    return {
        "status": "EXPERIMENTAL_RECOMMENDATION",
        "method": "upper Tukey fence: Q3 + 1.5 * IQR",
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "raw_anomaly_value_threshold": raw_threshold,
        "equivalent_minimum_normalized_score": normalized_threshold,
        "project_count": flagged_count,
        "project_rate": flagged_count / len(anomaly_values),
    }


def build_matrix(records, cohort, include_cost_ratio):
    """Builds a validated transformed matrix and project detail records."""
    matrix_rows = []
    details = []
    feature_order = None

    for record in records:
        original, transformed, current_order = transform_project(
            record, cohort, include_cost_ratio
        )
        if feature_order is None:
            feature_order = current_order
        elif feature_order != current_order:
            raise ValueError(f"Inconsistent feature order in cohort {cohort}")

        matrix_rows.append([transformed[name] for name in feature_order])
        details.append({
            "project_id": record["project_id"],
            "original_features": original,
            "transformed_features": transformed,
        })

    matrix = np.asarray(matrix_rows, dtype=float)
    if matrix.ndim != 2 or not np.all(np.isfinite(matrix)):
        raise ValueError(f"Invalid transformed matrix for cohort {cohort}")
    return matrix, details, feature_order


def fit_experiment(records, cohort, include_cost_ratio):
    """Fits one model and returns model, score, and per-project results."""
    matrix, details, feature_order = build_matrix(
        records, cohort, include_cost_ratio
    )
    model = IsolationForest(**MODEL_PARAMETERS)
    model.fit(matrix)

    raw_scores = model.score_samples(matrix)
    anomaly_values = -raw_scores
    percentile_scores = percentile_anomaly_scores(anomaly_values)

    project_results = []
    for detail, raw_score, anomaly_value, percentile_score in zip(
        details, raw_scores, anomaly_values, percentile_scores
    ):
        project_results.append({
            **detail,
            "raw_isolation_forest_score": float(raw_score),
            "raw_anomaly_value": float(anomaly_value),
            "cohort_percentile_anomaly_score": float(percentile_score),
        })

    ranked_results = sorted(
        project_results,
        key=lambda item: (
            item["raw_anomaly_value"], item["project_id"]
        ),
        reverse=True,
    )
    sensitivity = []
    for threshold in PERCENTILE_THRESHOLDS:
        flagged_count = sum(
            result["cohort_percentile_anomaly_score"] >= threshold
            for result in project_results
        )
        sensitivity.append({
            "threshold": threshold,
            "project_count": flagged_count,
            "project_rate": flagged_count / len(project_results),
        })

    return {
        "feature_names": feature_order,
        "project_count": len(project_results),
        "effective_max_samples": int(model.max_samples_),
        "raw_isolation_forest_score_distribution": distribution_summary(raw_scores),
        "raw_anomaly_value_distribution": distribution_summary(anomaly_values),
        "normalized_score_distribution": distribution_summary(percentile_scores),
        "recommended_threshold": recommend_distribution_threshold(
            anomaly_values, percentile_scores
        ),
        "threshold_sensitivity": sensitivity,
        "top_20": ranked_results[:20],
        "project_results": project_results,
    }


def compare_rankings(full_result, ablated_result):
    """Compares top-ranked projects between full and cost-ablated models."""
    full_ranked = sorted(
        full_result["project_results"],
        key=lambda item: item["raw_anomaly_value"],
        reverse=True,
    )
    ablated_ranked = sorted(
        ablated_result["project_results"],
        key=lambda item: item["raw_anomaly_value"],
        reverse=True,
    )
    comparisons = []

    counts = OVERLAP_COUNTS + [max(1, round(0.01 * len(full_ranked)))]
    for count in counts:
        full_ids = {item["project_id"] for item in full_ranked[:count]}
        ablated_ids = {item["project_id"] for item in ablated_ranked[:count]}
        overlap = len(full_ids & ablated_ids)
        comparisons.append({
            "top_count": count,
            "overlap_count": overlap,
            "overlap_rate": overlap / count,
        })
    return comparisons


def compact_project_results(full_result, ablated_result, cohort):
    """Combines both experimental scores while preserving every project."""
    ablated_by_id = {
        item["project_id"]: item
        for item in ablated_result["project_results"]
    }
    combined = []
    for item in full_result["project_results"]:
        ablated = ablated_by_id[item["project_id"]]
        combined.append({
            "project_id": item["project_id"],
            "cohort": cohort,
            "raw_isolation_forest_score": item["raw_isolation_forest_score"],
            "raw_anomaly_value": item["raw_anomaly_value"],
            "cohort_percentile_anomaly_score": item[
                "cohort_percentile_anomaly_score"
            ],
            "without_cost_ratio": {
                "raw_isolation_forest_score": ablated[
                    "raw_isolation_forest_score"
                ],
                "raw_anomaly_value": ablated["raw_anomaly_value"],
                "cohort_percentile_anomaly_score": ablated[
                    "cohort_percentile_anomaly_score"
                ],
            },
        })
    return combined


def strip_project_results(result):
    """Removes bulky intermediate results from a report section."""
    return {
        key: value
        for key, value in result.items()
        if key != "project_results"
    }


def run_experiment(records):
    """Runs full and cost-ratio ablation experiments for both cohorts."""
    cohorts = split_cohorts(records)
    report = {
        "experiment": "Isolation Forest Phase 3 - first experiment",
        "status": "EXPERIMENTAL",
        "source_path": FEATURES_PATH,
        "sklearn_version": sklearn.__version__,
        "model_parameters": MODEL_PARAMETERS,
        "percentile_normalization": {
            "reference": "frozen fitted cohort score distribution",
            "method": "empirical midrank percentile",
            "formula": "100 * zero_based_midrank / (cohort_size - 1)",
            "higher_means": "more anomalous",
        },
        "frozen_preprocessing": {
            "cost_ratio_caps": COST_RATIO_CAPS,
            "cohort_features": FEATURE_NAMES,
            "standardization": False,
        },
        "cohorts": {},
        "project_results": [],
    }

    for cohort in (COHORT_A, COHORT_B):
        full_result = fit_experiment(cohorts[cohort], cohort, True)
        ablated_result = fit_experiment(cohorts[cohort], cohort, False)
        report["cohorts"][cohort] = {
            "with_cost_ratio": strip_project_results(full_result),
            "without_cost_ratio": strip_project_results(ablated_result),
            "ranking_overlap": compare_rankings(full_result, ablated_result),
        }
        report["project_results"].extend(
            compact_project_results(full_result, ablated_result, cohort)
        )

    if len(report["project_results"]) != len(records):
        raise ValueError("Experiment did not preserve exactly one result per project")
    return report


def save_json(data, filepath):
    """Writes indented UTF-8 JSON, creating the output directory."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=FEATURES_PATH)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        records = load_json_list(args.features)
        report = run_experiment(records)
        save_json(report, args.output)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print("SUCCESS: Isolation Forest Phase 3 experiment complete.")
    print(f"Projects processed: {len(report['project_results'])}")
    for cohort, cohort_report in report["cohorts"].items():
        count = cohort_report["with_cost_ratio"]["project_count"]
        print(f"{cohort}: {count}")
    print(f"Output path: {args.output}")


if __name__ == "__main__":
    main()
