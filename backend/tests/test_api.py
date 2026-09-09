"""
tests/test_api.py
=================
API tests against the processed MPLADS project and risk dataset.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_json(path: str, expected_status: int = 200):
    """Requests JSON and checks the expected HTTP status."""
    response = client.get(path)
    assert response.status_code == expected_status, (
        f"Expected {expected_status} but got {response.status_code} for {path}. "
        f"Body: {response.text}"
    )
    return response.json()


class TestGetProjects:
    def test_default_page_uses_real_dataset(self):
        data = get_json("/api/projects")
        assert data["total"] == 78079
        assert data["page"] == 1
        assert data["pageSize"] == 50
        assert data["totalPages"] == 1562
        assert len(data["projects"]) == 50

    def test_each_project_has_existing_and_real_data_fields(self):
        data = get_json("/api/projects?page_size=2")
        required = [
            "projectId",
            "workName",
            "activityName",
            "description",
            "category",
            "state",
            "constituency",
            "mpName",
            "authority",
            "recommendationDate",
            "sanctionDate",
            "sanctionAmount",
            "workStage",
            "vendorName",
            "totalDisbursed",
            "lastExpenditureDate",
            "hasExpenditure",
            "expenditureRecordCount",
            "uniqueVendorCount",
            "vendors",
            "workIds",
            "officialWorkIds",
            "hasOfficialAttachment",
            "mlEligible",
            "mlStatus",
            "mlRawScore",
            "mlAnomalyValue",
            "mlAnomalyScore",
            "mlIsAnomaly",
            "mlAnomalyLevel",
            "mlRuleAgreement",
            "mlProjectAgeDays",
            "mlDaysToFirstExpenditure",
            "mlExpenditureRecordCount",
            "mlUniqueVendorCount",
            "mlDisbursementRatio",
            "mlWorkStage",
            "risk",
            "similarProjects",
        ]
        for project in data["projects"]:
            assert all(field in project for field in required)

    def test_risk_components_remain_explainable(self):
        project = get_json("/api/projects?page_size=1")["projects"][0]
        assert all(
            field in project["risk"]
            for field in [
                "overallScore",
                "level",
                "flagCount",
                "cost",
                "delay",
                "expenditure",
                "duplicate",
            ]
        )
        for detector in ["cost", "delay", "expenditure", "duplicate"]:
            assert set(project["risk"][detector]) == {"score", "flagged", "reason"}

    def test_second_page_is_distinct(self):
        first = get_json("/api/projects?page=1&page_size=2")
        second = get_json("/api/projects?page=2&page_size=2")
        first_ids = {project["projectId"] for project in first["projects"]}
        second_ids = {project["projectId"] for project in second["projects"]}
        assert first_ids.isdisjoint(second_ids)

    def test_page_size_limit_is_enforced(self):
        get_json("/api/projects?page=0", expected_status=422)
        get_json("/api/projects?page_size=101", expected_status=422)


class TestGetProjectById:
    def test_returns_real_project(self):
        data = get_json("/api/projects/133166")
        assert data["projectId"] == "133166"
        assert data["state"] == "Karnataka"
        assert data["risk"]["overallScore"] == 55.21
        assert data["risk"]["delay"]["flagged"] is True

    def test_similar_project_evidence_is_preserved(self):
        data = get_json("/api/projects/135168")
        similar = data["similarProjects"][0]
        assert similar["projectId"] == "135169"
        assert similar["dateDifferenceDays"] == 0
        assert similar["similarity"] is None

    def test_returns_404_for_nonexistent_project(self):
        data = get_json("/api/projects/does-not-exist", expected_status=404)
        assert data["detail"] == "Project not found"

    def test_100_score_exposes_combined_risk_evidence(self):
        data = get_json("/api/projects/134038")
        risk = data["risk"]
        assert risk["overallScore"] == 100
        assert risk["baseScore"] == 100
        assert risk["strongestDetector"] == "cost"
        assert risk["flagCount"] == 2
        assert risk["multiSignalBonus"] == 10
        assert risk["scoreCapped"] is True

    def test_completed_work_identifiers_are_separate_from_textual_work_ids(self):
        data = get_json("/api/projects/133312")
        assert data["workIds"] == ["WS/\t MP620/2024-2025/133312"]
        assert data["officialWorkIds"] == [58590]
        assert data["hasOfficialAttachment"] is True

    def test_eligible_project_exposes_frozen_numeric_ml_scores(self):
        data = get_json("/api/projects/133166")
        assert data["mlEligible"] is True
        assert data["mlStatus"] is None
        assert isinstance(data["mlRawScore"], float)
        assert isinstance(data["mlAnomalyValue"], float)
        assert isinstance(data["mlAnomalyScore"], float)

    def test_noneligible_project_preserves_not_applicable_and_null_scores(self):
        data = get_json("/api/projects/133167")
        assert data["mlEligible"] is False
        assert data["mlStatus"] == "ML_NOT_APPLICABLE"
        assert data["mlRawScore"] is None
        assert data["mlAnomalyValue"] is None
        assert data["mlAnomalyScore"] is None
        assert data["mlIsAnomaly"] is False

    def test_ml_agreement_values_are_preserved(self):
        assert get_json("/api/projects/137597")["mlRuleAgreement"] == "ML_ONLY"
        assert get_json("/api/projects/133697")["mlRuleAgreement"] == "BOTH_HIGH"

    def test_ml_anomaly_flag_is_not_inferred_from_display_level(self):
        data = get_json("/api/projects/134123")
        assert data["mlAnomalyLevel"] == "HIGH"
        assert data["mlIsAnomaly"] is False


class TestProjectFilters:
    def test_risk_filters_use_real_risk_levels(self):
        for requested, returned in [
            ("LOW", "LOW"),
            ("MODERATE", "MODERATE"),
            ("HIGH", "HIGH"),
            ("CRITICAL", "CRITICAL"),
        ]:
            data = get_json(f"/api/projects?risk={requested}&page_size=5")
            assert data["total"] > 0
            assert all(p["risk"]["level"] == returned for p in data["projects"])

    def test_legacy_medium_filter_maps_to_moderate(self):
        data = get_json("/api/projects?risk=MEDIUM&page_size=5")
        assert data["total"] > 0
        assert all(p["risk"]["level"] == "MODERATE" for p in data["projects"])

    def test_state_filter_is_case_insensitive_partial_match(self):
        data = get_json("/api/projects?state=karn&page_size=10")
        assert data["total"] > 0
        assert all("karn" in p["state"].lower() for p in data["projects"])

    def test_combined_filter_applies_before_pagination(self):
        data = get_json(
            "/api/projects?risk=HIGH&state=Karnataka&page=1&page_size=5"
        )
        assert data["total"] >= len(data["projects"])
        assert all(
            p["risk"]["level"] == "HIGH" and "karnataka" in p["state"].lower()
            for p in data["projects"]
        )

    def test_impossible_combination_returns_empty_page(self):
        data = get_json("/api/projects?risk=LOW&state=DoesNotExistState")
        assert data["total"] == 0
        assert data["totalPages"] == 0
        assert data["projects"] == []

    def test_category_filter_is_applied_server_side(self):
        options = get_json("/api/projects/options")
        category = options["categories"][0]
        data = get_json(f"/api/projects?category={category}&page_size=5")
        assert data["total"] > 0
        assert all(p["category"].lower() == category.lower() for p in data["projects"])

    def test_search_is_applied_server_side(self):
        data = get_json("/api/projects?search=133166&page_size=5")
        assert data["total"] == 1
        assert data["projects"][0]["projectId"] == "133166"

    def test_search_is_case_insensitive(self):
        lower = get_json("/api/projects?search=karnataka&page_size=5")
        upper = get_json("/api/projects?search=KARNATAKA&page_size=5")
        assert lower["total"] == upper["total"] > 0
        assert [project["projectId"] for project in lower["projects"]] == [
            project["projectId"] for project in upper["projects"]
        ]

    def test_partial_search(self):
        data = get_json("/api/projects?search=13316&page_size=5")
        assert data["total"] > 0
        assert data["projects"][0]["projectId"].startswith("13316")

    def test_multi_word_search_allows_any_order(self):
        forward = get_json("/api/projects?search=Pralhad%20Joshi&page_size=5")
        reverse = get_json("/api/projects?search=Joshi%20Pralhad&page_size=5")
        assert forward["total"] == reverse["total"] == 125
        assert [project["projectId"] for project in forward["projects"]] == [
            project["projectId"] for project in reverse["projects"]
        ]

    def test_street_light_alias_search(self):
        data = get_json("/api/projects?search=street%20light&page_size=10")
        assert data["total"] > 0
        assert data["projects"]

    def test_bridge_alias_search(self):
        data = get_json("/api/projects?search=bridge&page_size=10")
        assert data["total"] > 0
        assert data["projects"]

    def test_road_alias_search(self):
        data = get_json("/api/projects?search=road&page_size=10")
        assert data["total"] > 0
        assert data["projects"]

    def test_search_by_mp_name_is_global(self):
        data = get_json(
            "/api/projects?search=Pralhad%20Venkatesh%20Joshi&page_size=5"
        )
        assert data["total"] == 125
        assert all(
            project["mpName"] == "Pralhad Venkatesh Joshi"
            for project in data["projects"]
        )

    def test_search_by_state_is_global(self):
        data = get_json("/api/projects?search=Karnataka&page_size=5")
        assert data["total"] >= 2596
        assert all(project["state"] == "Karnataka" for project in data["projects"])

    def test_search_by_vendor_is_global(self):
        data = get_json(
            "/api/projects?search=SHRINIVAS%20MAVINAKAI&page_size=5"
        )
        assert data["total"] > 0
        assert all("mavinakai" in project["vendorName"].lower() for project in data["projects"])

    def test_search_includes_work_ids(self):
        response = client.get(
            "/api/projects",
            params={
                "search": "WS/ MP620/2024-2025/133166",
                "page_size": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["projects"][0]["projectId"] == "133166"

    def test_combined_search_and_filters_use_full_dataset(self):
        response = client.get(
            "/api/projects",
            params={
                "search": "Pralhad Venkatesh Joshi",
                "state": "Karnataka",
                "risk": "HIGH",
                "page_size": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 12
        assert len(data["projects"]) == 5
        assert all(
            project["mpName"] == "Pralhad Venkatesh Joshi"
            and project["state"] == "Karnataka"
            and project["risk"]["level"] == "HIGH"
            for project in data["projects"]
        )

    def test_search_state_category_and_risk_filters_compose(self):
        category = get_json(
            "/api/projects?search=road&state=Karnataka&risk=HIGH&page_size=1"
        )["projects"][0]["category"]
        response = client.get(
            "/api/projects",
            params={
                "search": "road",
                "state": "Karnataka",
                "category": category,
                "risk": "HIGH",
                "page_size": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert all(
            project["state"] == "Karnataka"
            and project["category"] == category
            and project["risk"]["level"] == "HIGH"
            for project in data["projects"]
        )

    def test_filter_options_come_from_real_data(self):
        data = get_json("/api/projects/options")
        assert "Karnataka" in data["states"]
        assert data["categories"]
        assert data["riskLevels"] == ["CRITICAL", "HIGH", "MODERATE", "LOW"]

    def test_ml_filters_use_frozen_artifact_fields(self):
        assert get_json("/api/projects?ml_eligible=false&page_size=1")["total"] == 22423
        assert get_json("/api/projects?ml_is_anomaly=true&page_size=1")["total"] == 1799
        assert get_json("/api/projects?ml_rule_agreement=ML_ONLY&page_size=1")["total"] == 227
        elevated = get_json(
            "/api/projects?ml_anomaly_level=HIGH&ml_is_anomaly=false&page_size=5"
        )
        assert elevated["total"] > 0
        assert all(
            project["mlAnomalyLevel"] == "HIGH"
            and project["mlIsAnomaly"] is False
            for project in elevated["projects"]
        )


class TestAlerts:
    def test_alerts_are_paginated(self):
        data = get_json("/api/alerts?page=1&page_size=10")
        assert data["total"] == 17774
        assert data["page"] == 1
        assert data["pageSize"] == 10
        assert data["totalPages"] == 1778
        assert len(data["alerts"]) == 10

    def test_alerts_reuse_detector_flags(self):
        data = get_json("/api/alerts?page_size=10")
        required = {
            "projectId",
            "workName",
            "state",
            "constituency",
            "mpName",
            "riskLevel",
            "overallScore",
            "flaggedDetectors",
        }
        for alert in data["alerts"]:
            assert required.issubset(alert)
            assert alert["flaggedDetectors"]

    def test_alert_page_size_limit_is_enforced(self):
        get_json("/api/alerts?page_size=101", expected_status=422)


class TestStatistics:
    def test_statistics_match_real_risk_distribution(self):
        data = get_json("/api/statistics")
        assert data == {
            "totalProjects": 78079,
            "highRisk": 6717,
            "mediumRisk": 10787,
            "lowRisk": 49518,
            "criticalRisk": 11057,
        }

    def test_statistics_match_filtered_totals(self):
        stats = get_json("/api/statistics")
        assert stats["highRisk"] == get_json("/api/projects?risk=HIGH")["total"]
        assert stats["mediumRisk"] == get_json("/api/projects?risk=MODERATE")["total"]
        assert stats["lowRisk"] == get_json("/api/projects?risk=LOW")["total"]
        assert stats["criticalRisk"] == get_json("/api/projects?risk=CRITICAL")["total"]

    def test_risk_counts_sum_to_total(self):
        data = get_json("/api/statistics")
        assert (
            data["highRisk"]
            + data["mediumRisk"]
            + data["lowRisk"]
            + data["criticalRisk"]
            == data["totalProjects"]
        )


class TestProjectAggregates:
    def test_nationwide_aggregates_cover_all_projects_and_states(self):
        data = get_json("/api/projects/aggregates")
        assert data["totalProjects"] == 78079
        assert data["totalSanctionAmount"] == 41069314737.08
        assert data["totalExpenditure"] == 27287454970.45
        assert data["riskLevelCounts"] == {
            "low": 49518,
            "moderate": 10787,
            "high": 6717,
            "critical": 11057,
        }
        assert data["requiresReviewCount"] == 17774
        assert data["flaggedComponentCounts"] == {
            "cost": 6040,
            "delay": 1477,
            "expenditure": 5538,
            "duplicate": 6724,
        }
        assert data["mlEligibleCount"] == 55656
        assert data["mlAnomalyCount"] == 1799
        assert data["mlNotApplicableCount"] == 22423
        assert data["mlOnlyCount"] == 227
        assert data["bothHighCount"] == 1572
        assert len(data["stateAggregates"]) == 36
        assert sum(state["projectCount"] for state in data["stateAggregates"]) == 78079

    def test_filtered_aggregates_match_complete_filtered_listing(self):
        params = {
            "search": "Pralhad Venkatesh Joshi",
            "state": "Karnataka",
            "risk": "HIGH",
        }
        aggregate_response = client.get("/api/projects/aggregates", params=params)
        list_response = client.get(
            "/api/projects", params={**params, "page": 1, "page_size": 5}
        )
        assert aggregate_response.status_code == 200
        assert list_response.status_code == 200
        aggregates = aggregate_response.json()
        listing = list_response.json()
        assert aggregates["totalProjects"] == listing["total"] == 12
        assert sum(aggregates["riskLevelCounts"].values()) == 12
        assert sum(state["projectCount"] for state in aggregates["stateAggregates"]) == 12
        assert aggregates["riskLevelCounts"]["high"] == 12

    def test_ml_filter_aggregates_cover_the_complete_matching_set(self):
        params = {"ml_rule_agreement": "ML_ONLY"}
        aggregates = client.get("/api/projects/aggregates", params=params).json()
        listing = client.get(
            "/api/projects", params={**params, "page_size": 5}
        ).json()
        assert aggregates["totalProjects"] == listing["total"] == 227
        assert aggregates["mlEligibleCount"] == 227
        assert aggregates["mlAnomalyCount"] == 227
        assert aggregates["mlOnlyCount"] == 227
        assert aggregates["mlNotApplicableCount"] == 0
        assert aggregates["bothHighCount"] == 0

    def test_table_page_changes_do_not_change_aggregates(self):
        params = {"search": "Karnataka"}
        before = client.get("/api/projects/aggregates", params=params).json()
        first_page = client.get(
            "/api/projects", params={**params, "page": 1, "page_size": 5}
        ).json()
        second_page = client.get(
            "/api/projects", params={**params, "page": 2, "page_size": 5}
        ).json()
        after = client.get("/api/projects/aggregates", params=params).json()

        assert first_page["projects"] != second_page["projects"]
        assert first_page["total"] == second_page["total"] == before["totalProjects"]
        assert before == after


class TestFactorAnalytics:
    def test_nationwide_factor_ranking_uses_detector_scores(self):
        data = get_json("/api/projects/analytics/factors/delay")
        assert data["factor"] == "delay"
        assert len(data["stateMetrics"]) == 36
        assert sum(row["totalProjects"] for row in data["stateMetrics"]) == 78079
        assert sum(row["flaggedProjects"] for row in data["stateMetrics"]) == 1477
        assert [row["averageScore"] for row in data["stateMetrics"]] == sorted(
            (row["averageScore"] for row in data["stateMetrics"]), reverse=True
        )

    def test_state_distribution_uses_native_detector_bands(self):
        data = get_json(
            "/api/projects/analytics/factors/cost?state=Karnataka"
        )
        assert data["stateMetrics"] == [
            {
                "state": "Karnataka",
                "averageScore": 13.34,
                "flaggedProjects": 334,
                "totalProjects": 2596,
            }
        ]
        assert [band["label"] for band in data["scoreBands"]] == [
            "0-19", "20-49", "50-79", "80-100"
        ]
        assert sum(band["projectCount"] for band in data["scoreBands"]) == 2596
        assert data["scoredProjects"] == 2596
        assert data["unscoredProjects"] == 0
        assert data["outOfRangeProjects"] == 0

    def test_unknown_factor_is_rejected(self):
        get_json(
            "/api/projects/analytics/factors/ml",
            expected_status=422,
        )

    def test_expenditure_distribution_excludes_not_applicable_projects(self):
        data = get_json("/api/projects/analytics/factors/expenditure")
        assert data["scoredProjects"] == 55656
        assert data["unscoredProjects"] == 22423
        assert sum(band["projectCount"] for band in data["scoreBands"]) == 55656


class TestProjectExport:
    def test_export_uses_the_same_filtered_result_set(self):
        params = {
            "search": "Pralhad Venkatesh Joshi",
            "state": "Karnataka",
            "risk": "HIGH",
        }
        response = client.get("/api/projects/export", params=params)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        lines = response.text.strip().splitlines()
        assert len(lines) == 13
        assert lines[0].startswith("project_id,work_name,state")
        assert all(",Karnataka," in line for line in lines[1:])
