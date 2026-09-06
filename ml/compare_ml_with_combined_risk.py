"""
ml/compare_ml_with_combined_risk.py

Compares the experimental Phase 3 Isolation Forest scores with the frozen
Combined Risk V1 output. This script is analysis-only: it does not retrain a
model, alter rule scores, or produce the final ML anomaly dataset.
"""

import json
import math
import os
import re
import sys
from collections import Counter, defaultdict


FEATURES_PATH = os.path.join("data", "processed", "features.json")
PROJECTS_PATH = os.path.join("data", "processed", "projects.json")
COMBINED_RISK_PATH = os.path.join("data", "processed", "combined_risk.json")
PHASE3_PATH = os.path.join(
    "data", "processed", "experiments", "isolation_forest_phase3.json"
)
OUTPUT_PATH = os.path.join(
    "data", "processed", "experiments", "ml_vs_combined_risk_phase4.json"
)

COHORT_A = "NO_EXPENDITURE"
COHORT_B = "HAS_EXPENDITURE"
RULE_ANOMALY_THRESHOLD = 50
TINY_AMOUNT_THRESHOLD = 1000
COMPONENTS = ("cost", "delay", "expenditure", "duplicate")

CONFIGURATIONS = {
    "CONFIGURATION_1_HYBRID": {
        COHORT_A: "with_cost_ratio",
        COHORT_B: "without_cost_ratio",
    },
    "CONFIGURATION_2_BEHAVIORAL_ONLY": {
        COHORT_B: "without_cost_ratio",
    },
}

SOURCE_FEATURES = {
    COHORT_A: (
        "sanction_amount",
        "days_since_sanction",
        "cost_vs_activity_median",
    ),
    COHORT_B: (
        "sanction_amount",
        "days_since_sanction",
        "disbursement_ratio",
        "expenditure_record_count",
        "unique_vendor_count",
        "days_to_first_expenditure",
    ),
}


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
    values = sorted(float(value) for value in values)
    if not values:
        raise ValueError("Cannot calculate a percentile for an empty list")
    position = (len(values) - 1) * percentile / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    fraction = position - lower
    return values[lower] + fraction * (values[upper] - values[lower])


def distribution_summary(values):
    """Returns compact distribution statistics."""
    return {
        "min": min(values),
        "median": linear_percentile(values, 50),
        "p95": linear_percentile(values, 95),
        "p99": linear_percentile(values, 99),
        "max": max(values),
    }


def calculate_tukey_threshold(anomaly_values):
    """Recalculates the upper Tukey threshold from a frozen score list."""
    q1 = linear_percentile(anomaly_values, 25)
    q3 = linear_percentile(anomaly_values, 75)
    iqr = q3 - q1
    return {
        "method": "upper Tukey fence: Q3 + 1.5 * IQR",
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "raw_anomaly_value_threshold": q3 + 1.5 * iqr,
    }


def validate_inputs(features, projects, risks, phase3):
    """Validates project coverage and frozen rule/component structures."""
    expected_ids = set(features)
    for label, records in (
        ("projects", projects),
        ("combined risk", risks),
    ):
        if set(records) != expected_ids:
            raise ValueError(f"Project IDs do not match between features and {label}")

    phase3_results = phase3.get("project_results")
    if not isinstance(phase3_results, list):
        raise ValueError("Phase 3 project_results must be a list")
    phase3_by_id = index_unique(phase3_results, "Phase 3 results")
    if set(phase3_by_id) != expected_ids:
        raise ValueError("Project IDs do not match between features and Phase 3")

    for project_id, risk in risks.items():
        overall_score = risk.get("overall_score")
        if not isinstance(overall_score, (int, float)):
            raise ValueError(f"Project {project_id} has invalid overall_score")
        for component in COMPONENTS:
            value = risk.get(component)
            if not isinstance(value, dict):
                raise ValueError(f"Project {project_id} lacks {component} result")
            if not isinstance(value.get("score"), (int, float)):
                raise ValueError(
                    f"Project {project_id} has invalid {component} score"
                )
            if not isinstance(value.get("flagged"), bool):
                raise ValueError(
                    f"Project {project_id} has invalid {component} flag"
                )
    return phase3_by_id


def build_structural_counts(features):
    """Counts exact operational signatures without description text."""
    counts = Counter()
    for record in features.values():
        counts[get_signature(record)] += 1
    return counts


def get_signature(record):
    """Returns the exact operational signature used for review."""
    return (
        record.get("normalized_activity_name"),
        record.get("state_name"),
        record.get("sanction_date"),
        record.get("sanction_amount"),
        record.get("work_stage"),
        record.get("has_expenditure"),
        record.get("expenditure_record_count"),
        record.get("total_disbursed"),
        record.get("unique_vendor_count"),
        record.get("first_expenditure_date"),
        record.get("last_expenditure_date"),
    )


def build_cohort_bounds(features, phase3_by_id):
    """Calculates descriptive P1/P99 boundaries for observable explanations."""
    grouped = defaultdict(list)
    for project_id, record in features.items():
        grouped[phase3_by_id[project_id]["cohort"]].append(record)

    fields = {
        COHORT_A: SOURCE_FEATURES[COHORT_A],
        COHORT_B: SOURCE_FEATURES[COHORT_B],
    }
    bounds = {}
    for cohort, records in grouped.items():
        bounds[cohort] = {}
        for field in fields[cohort]:
            values = [record[field] for record in records]
            bounds[cohort][field] = {
                "p1": linear_percentile(values, 1),
                "p99": linear_percentile(values, 99),
            }
    return bounds


def select_ml_score(phase3_result, mode):
    """Selects the approved full or ablated Phase 3 score fields."""
    if mode == "with_cost_ratio":
        return {
            "raw_isolation_forest_score": phase3_result[
                "raw_isolation_forest_score"
            ],
            "raw_anomaly_value": phase3_result["raw_anomaly_value"],
            "ml_anomaly_score": phase3_result[
                "cohort_percentile_anomaly_score"
            ],
        }
    ablated = phase3_result["without_cost_ratio"]
    return {
        "raw_isolation_forest_score": ablated["raw_isolation_forest_score"],
        "raw_anomaly_value": ablated["raw_anomaly_value"],
        "ml_anomaly_score": ablated["cohort_percentile_anomaly_score"],
    }


def threshold_for_mode(phase3, cohort, mode, phase3_by_id):
    """Loads and independently verifies the selected model's Tukey threshold."""
    saved = phase3["cohorts"][cohort][mode]["recommended_threshold"]
    values = []
    selected_scores = []
    for result in phase3_by_id.values():
        if result["cohort"] != cohort:
            continue
        score = select_ml_score(result, mode)
        values.append(score["raw_anomaly_value"])
        selected_scores.append(score)

    recalculated = calculate_tukey_threshold(values)
    saved_threshold = saved["raw_anomaly_value_threshold"]
    if not math.isclose(
        saved_threshold,
        recalculated["raw_anomaly_value_threshold"],
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise ValueError(f"Saved and recalculated thresholds differ for {cohort}")

    flagged_scores = [
        score["ml_anomaly_score"]
        for score in selected_scores
        if score["raw_anomaly_value"] >= saved_threshold
    ]
    return {
        **recalculated,
        "equivalent_minimum_normalized_score": min(flagged_scores),
        "verified_against_phase3": True,
    }


def observable_reasons(feature, cohort, bounds, risk):
    """Describes empirical feature extremes without asserting causation."""
    reasons = []
    cohort_bounds = bounds[cohort]

    def high(field, label):
        if feature[field] >= cohort_bounds[field]["p99"]:
            reasons.append(
                f"{label} {feature[field]:g} is at or above cohort P99 "
                f"({cohort_bounds[field]['p99']:g})"
            )

    def low(field, label):
        if feature[field] <= cohort_bounds[field]["p1"]:
            reasons.append(
                f"{label} {feature[field]:g} is at or below cohort P1 "
                f"({cohort_bounds[field]['p1']:g})"
            )

    high("sanction_amount", "Sanction amount")
    low("sanction_amount", "Sanction amount")
    high("days_since_sanction", "Project age in days")
    low("days_since_sanction", "Project age in days")

    if cohort == COHORT_A:
        high("cost_vs_activity_median", "Activity cost ratio")
        low("cost_vs_activity_median", "Activity cost ratio")
    else:
        low("disbursement_ratio", "Disbursement ratio")
        high("expenditure_record_count", "Expenditure record count")
        high("unique_vendor_count", "Unique vendor count")
        high("days_to_first_expenditure", "Days to first expenditure")
        if feature["days_to_first_expenditure"] == 0:
            reasons.append("First expenditure is recorded on the sanction date")

    if all(risk[component]["score"] < RULE_ANOMALY_THRESHOLD for component in COMPONENTS):
        reasons.append("No individual rule component reached 50")
    if len(reasons) == 1 and reasons[0] == "No individual rule component reached 50":
        reasons.insert(
            0,
            "Isolation arises from the joint feature position; no selected feature "
            "individually crosses its P1/P99 boundary",
        )
    return reasons


def feature_pattern_labels(feature, cohort, bounds):
    """Returns non-exclusive empirical pattern labels for aggregate analysis."""
    cohort_bounds = bounds[cohort]
    amount_extreme = (
        feature["sanction_amount"] <= cohort_bounds["sanction_amount"]["p1"]
        or feature["sanction_amount"] >= cohort_bounds["sanction_amount"]["p99"]
    )
    age_extreme = (
        feature["days_since_sanction"]
        <= cohort_bounds["days_since_sanction"]["p1"]
        or feature["days_since_sanction"]
        >= cohort_bounds["days_since_sanction"]["p99"]
    )
    labels = []
    if amount_extreme:
        labels.append("unusual_sanction_amount")
    if age_extreme:
        labels.append("unusual_project_age")
    if amount_extreme and age_extreme:
        labels.append("unusual_amount_age_combination")

    if cohort == COHORT_A:
        ratio = feature["cost_vs_activity_median"]
        ratio_bounds = cohort_bounds["cost_vs_activity_median"]
        if ratio <= ratio_bounds["p1"] or ratio >= ratio_bounds["p99"]:
            labels.append("unusual_peer_cost_ratio")
    else:
        if (
            feature["disbursement_ratio"]
            <= cohort_bounds["disbursement_ratio"]["p1"]
        ):
            labels.append("unusual_disbursement_ratio")
        if (
            feature["expenditure_record_count"]
            >= cohort_bounds["expenditure_record_count"]["p99"]
        ):
            labels.append("unusual_payment_count")
        if (
            feature["unique_vendor_count"]
            >= cohort_bounds["unique_vendor_count"]["p99"]
        ):
            labels.append("unusual_vendor_count")
        first_days = feature["days_to_first_expenditure"]
        if (
            first_days == 0
            or first_days
            >= cohort_bounds["days_to_first_expenditure"]["p99"]
        ):
            labels.append("unusual_expenditure_timing")

    if not labels:
        labels.append("joint_pattern_without_individual_p1_p99_extreme")
    return labels


def review_flags(feature, project, risk, cohort, bounds, structural_counts):
    """Flags conservative metadata/data-quality concerns for manual review."""
    flags = []
    amount = feature["sanction_amount"]
    if amount < TINY_AMOUNT_THRESHOLD:
        flags.append("SUSPICIOUSLY_TINY_MONETARY_VALUE")
    if not str(feature.get("work_description") or "").strip():
        flags.append("MISSING_WORK_DESCRIPTION")
    if not str(feature.get("normalized_activity_name") or "").strip():
        flags.append("MISSING_ACTIVITY")

    signature_count = structural_counts[get_signature(feature)]
    if signature_count > 1:
        flags.append(f"REPEATED_EXACT_OPERATIONAL_STRUCTURE_COUNT_{signature_count}")
    if 0 < risk["duplicate"]["score"] < RULE_ANOMALY_THRESHOLD:
        flags.append("SUBTHRESHOLD_DUPLICATE_RULE_SIGNAL")

    if feature["days_since_sanction"] <= bounds[cohort]["days_since_sanction"]["p1"]:
        flags.append("VERY_RECENT_PROJECT_LIFECYCLE_CONTEXT")
    if cohort == COHORT_A and feature["days_since_sanction"] <= 30:
        flags.append("NO_EXPENDITURE_MAY_REFLECT_EARLY_LIFECYCLE")
    if (
        cohort == COHORT_B
        and str(feature.get("work_stage") or "").strip().lower()
        == "vendor identification"
    ):
        flags.append("EXPENDITURE_WITH_VENDOR_IDENTIFICATION_STAGE")
    if (
        cohort == COHORT_B
        and feature.get("first_expenditure_date")
        and feature.get("first_expenditure_date") == feature.get("sanction_date")
    ):
        flags.append("SAME_DAY_SANCTION_AND_FIRST_EXPENDITURE")
    description = str(feature.get("work_description") or "")
    if re.search(r"(?<!\d)\d{10}(?!\d)", description):
        flags.append("SOURCE_DESCRIPTION_CONTAINS_PHONE_LIKE_TEXT")

    malformed_fields = []
    for field in SOURCE_FEATURES[cohort]:
        value = feature.get(field)
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            malformed_fields.append(field)
    if malformed_fields:
        flags.append("MALFORMED_ML_FIELDS:" + ",".join(malformed_fields))

    if not flags:
        flags.append("NO_OBVIOUS_METADATA_OR_DATA_QUALITY_FLAG")
    return {
        "flags": flags,
        "exact_structural_record_count": signature_count,
        "metadata": {
            "activity_name": feature.get("normalized_activity_name"),
            "work_category": feature.get("work_category"),
            "state_name": feature.get("state_name"),
            "sanction_date": feature.get("sanction_date"),
            "first_expenditure_date": feature.get("first_expenditure_date"),
            "last_expenditure_date": feature.get("last_expenditure_date"),
            "work_stage": feature.get("work_stage"),
            "project_dataset_record_present": project is not None,
        },
    }


def build_top_record(
    project_id,
    cohort,
    score,
    feature,
    project,
    risk,
    mode,
    bounds,
    structural_counts,
):
    """Builds a detailed top-ML-only review record."""
    original_features = {
        field: feature[field]
        for field in SOURCE_FEATURES[cohort]
    }
    transformed = {
        "log1p_sanction_amount": math.log1p(feature["sanction_amount"]),
        "days_since_sanction": feature["days_since_sanction"],
    }
    if cohort == COHORT_A:
        transformed["clipped_log1p_cost_vs_activity_median"] = math.log1p(
            min(feature["cost_vs_activity_median"], 12.331741)
        )
    else:
        transformed.update({
            "disbursement_ratio": feature["disbursement_ratio"],
            "log1p_expenditure_record_count": math.log1p(
                feature["expenditure_record_count"]
            ),
            "log1p_unique_vendor_count": math.log1p(
                feature["unique_vendor_count"]
            ),
            "log1p_days_to_first_expenditure": math.log1p(
                feature["days_to_first_expenditure"]
            ),
        })

    review = review_flags(
        feature, project, risk, cohort, bounds, structural_counts
    )
    return {
        "project_id": project_id,
        "cohort": cohort,
        "model_mode": mode,
        **score,
        "overall_risk_score": risk["overall_score"],
        "component_scores": {
            component: risk[component]["score"]
            for component in COMPONENTS
        },
        "original_ml_features": original_features,
        "transformed_ml_features": transformed,
        "observable_reasons": observable_reasons(
            feature, cohort, bounds, risk
        ),
        "manual_metadata_review": review,
    }


def evaluate_configuration(
    name,
    modes,
    features,
    projects,
    risks,
    phase3,
    phase3_by_id,
    bounds,
    structural_counts,
):
    """Evaluates one approved ML eligibility/model configuration."""
    thresholds = {
        cohort: threshold_for_mode(phase3, cohort, mode, phase3_by_id)
        for cohort, mode in modes.items()
    }
    outcomes = []
    category_counts = Counter()
    category_by_cohort = defaultdict(Counter)
    component_agreement = Counter()
    ml_only_rule_bands = Counter()
    ml_only_feature_patterns = Counter()
    rule_only_ml_scores = []
    top_candidates = []

    for project_id, feature in features.items():
        phase3_result = phase3_by_id[project_id]
        cohort = phase3_result["cohort"]
        risk = risks[project_id]
        rule_high = risk["overall_score"] >= RULE_ANOMALY_THRESHOLD

        if cohort not in modes:
            outcomes.append({
                "project_id": project_id,
                "cohort": cohort,
                "ml_status": "ML_NOT_APPLICABLE",
                "rule_high": rule_high,
            })
            continue

        mode = modes[cohort]
        score = select_ml_score(phase3_result, mode)
        ml_high = score["raw_anomaly_value"] >= thresholds[cohort][
            "raw_anomaly_value_threshold"
        ]
        if ml_high and rule_high:
            category = "BOTH_HIGH"
        elif ml_high:
            category = "ML_ONLY"
        elif rule_high:
            category = "RULE_ONLY"
        else:
            category = "NEITHER"

        category_counts[category] += 1
        category_by_cohort[cohort][category] += 1
        outcomes.append({
            "project_id": project_id,
            "cohort": cohort,
            "ml_status": "ML_ANOMALY" if ml_high else "ML_NOT_ANOMALOUS",
            "comparison_category": category,
            "rule_high": rule_high,
            **score,
        })

        if ml_high:
            for component in COMPONENTS:
                if risk[component]["flagged"]:
                    component_agreement[component] += 1
        if category == "ML_ONLY":
            band = "0-19" if risk["overall_score"] < 20 else "20-49"
            ml_only_rule_bands[band] += 1
            ml_only_feature_patterns.update(
                feature_pattern_labels(feature, cohort, bounds)
            )
            top_candidates.append(build_top_record(
                project_id,
                cohort,
                score,
                feature,
                projects[project_id],
                risk,
                mode,
                bounds,
                structural_counts,
            ))
        elif category == "RULE_ONLY":
            rule_only_ml_scores.append(score["ml_anomaly_score"])

    eligible_count = sum(category_counts.values())
    ml_anomaly_count = category_counts["BOTH_HIGH"] + category_counts["ML_ONLY"]
    eligible_rule_count = category_counts["BOTH_HIGH"] + category_counts["RULE_ONLY"]
    total_rule_count = sum(
        risk["overall_score"] >= RULE_ANOMALY_THRESHOLD
        for risk in risks.values()
    )
    top_candidates.sort(
        # Percentile scores, unlike raw values from separate cohort models,
        # are comparable across cohorts.
        key=lambda item: (
            item["ml_anomaly_score"],
            item["raw_anomaly_value"],
            item["project_id"],
        ),
        reverse=True,
    )

    return {
        "name": name,
        "eligible_ml_project_count": eligible_count,
        "not_applicable_project_count": len(features) - eligible_count,
        "ml_anomaly_count": ml_anomaly_count,
        "ml_anomaly_rate": ml_anomaly_count / eligible_count,
        "rule_engine_all_projects": {
            "project_count": len(risks),
            "anomaly_count": total_rule_count,
            "anomaly_rate": total_rule_count / len(risks),
        },
        "rule_engine_among_ml_eligible": {
            "anomaly_count": eligible_rule_count,
            "anomaly_rate": eligible_rule_count / eligible_count,
        },
        "comparison_counts": dict(category_counts),
        "comparison_rates": {
            category: count / eligible_count
            for category, count in category_counts.items()
        },
        "ml_only_share_of_ml_anomalies": (
            category_counts["ML_ONLY"] / ml_anomaly_count
        ),
        "rule_corroborated_share_of_ml_anomalies": (
            category_counts["BOTH_HIGH"] / ml_anomaly_count
        ),
        "both_high_and_ml_only_by_cohort": {
            cohort: {
                "BOTH_HIGH": counts["BOTH_HIGH"],
                "ML_ONLY": counts["ML_ONLY"],
            }
            for cohort, counts in category_by_cohort.items()
        },
        "ml_only_rule_score_distribution": {
            "0-19": ml_only_rule_bands["0-19"],
            "20-49": ml_only_rule_bands["20-49"],
        },
        "ml_only_feature_pattern_counts": {
            label: {
                "project_count": count,
                "project_rate_among_ml_only": (
                    count / category_counts["ML_ONLY"]
                ),
            }
            for label, count in sorted(ml_only_feature_patterns.items())
        },
        "rule_only_ml_score_distribution": distribution_summary(
            rule_only_ml_scores
        ) if rule_only_ml_scores else None,
        "component_agreement_among_ml_anomalies": {
            component: {
                "project_count": component_agreement[component],
                "project_rate": component_agreement[component] / ml_anomaly_count,
            }
            for component in COMPONENTS
        },
        "thresholds": thresholds,
        "top_20_ml_only": top_candidates[:20],
        "project_outcomes": outcomes,
    }


def run_comparison():
    """Loads inputs and evaluates both Phase 4 configurations."""
    feature_records = load_json(FEATURES_PATH, list)
    project_records = load_json(PROJECTS_PATH, list)
    risk_records = load_json(COMBINED_RISK_PATH, list)
    phase3 = load_json(PHASE3_PATH, dict)

    features = index_unique(feature_records, "features")
    projects = index_unique(project_records, "projects")
    risks = index_unique(risk_records, "combined risk")
    phase3_by_id = validate_inputs(features, projects, risks, phase3)
    bounds = build_cohort_bounds(features, phase3_by_id)
    structural_counts = build_structural_counts(features)

    report = {
        "experiment": "Phase 4 ML comparison with Combined Risk V1",
        "status": "EXPERIMENTAL",
        "rule_anomaly_definition": "overall_score >= 50",
        "source_paths": {
            "features": FEATURES_PATH,
            "projects": PROJECTS_PATH,
            "combined_risk": COMBINED_RISK_PATH,
            "phase3": PHASE3_PATH,
        },
        "observable_reason_percentile_bounds": bounds,
        "configurations": {},
    }
    for name, modes in CONFIGURATIONS.items():
        report["configurations"][name] = evaluate_configuration(
            name,
            modes,
            features,
            projects,
            risks,
            phase3,
            phase3_by_id,
            bounds,
            structural_counts,
        )
    return report


def save_json(data, filepath):
    """Writes indented UTF-8 JSON, creating its output directory."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    try:
        report = run_comparison()
        save_json(report, OUTPUT_PATH)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print("SUCCESS: Phase 4 experimental comparison complete.")
    for name, result in report["configurations"].items():
        print(
            f"{name}: {result['eligible_ml_project_count']} eligible, "
            f"{result['ml_anomaly_count']} ML anomalies"
        )
    print(f"Output path: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
