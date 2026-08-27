"""
tests/test_api.py
==================
Basic pytest test suite for the MPLADS Risk Intelligence System API.

Tests cover:
  - GET /api/projects            (all projects)
  - GET /api/projects/{id}       (single project)
  - GET /api/projects/nonexistent → 404
  - GET /api/projects?risk=HIGH  (risk filter)
  - GET /api/projects?state=Karnataka  (state filter)
  - GET /api/projects?risk=HIGH&state=Karnataka  (combined filter)
  - GET /api/alerts
  - GET /api/statistics          (dynamic consistency check)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_json(path: str, expected_status: int = 200):
    response = client.get(path)
    assert response.status_code == expected_status, (
        f"Expected {expected_status} but got {response.status_code} for {path}. "
        f"Body: {response.text}"
    )
    return response.json()


# ---------------------------------------------------------------------------
# GET /api/projects — all projects
# ---------------------------------------------------------------------------

class TestGetAllProjects:
    def test_returns_200(self):
        response = client.get("/api/projects")
        assert response.status_code == 200

    def test_response_has_total_and_projects(self):
        data = get_json("/api/projects")
        assert "total" in data
        assert "projects" in data

    def test_total_matches_projects_list_length(self):
        data = get_json("/api/projects")
        assert data["total"] == len(data["projects"])

    def test_returns_all_20_mock_records(self):
        data = get_json("/api/projects")
        assert data["total"] == 20

    def test_each_project_has_required_fields(self):
        data = get_json("/api/projects")
        required = [
            "projectId", "workName", "description", "category", "state",
            "constituency", "mpName", "authority", "recommendationDate",
            "sanctionDate", "sanctionAmount", "workStage", "vendorName",
            "totalDisbursed", "lastExpenditureDate", "risk", "similarProjects",
        ]
        for project in data["projects"]:
            for field in required:
                assert field in project, f"Missing field '{field}' in project {project.get('projectId')}"

    def test_risk_block_has_required_fields(self):
        data = get_json("/api/projects")
        risk_fields = ["overallScore", "level", "cost", "delay", "expenditure", "duplicate"]
        for project in data["projects"]:
            risk = project["risk"]
            for field in risk_fields:
                assert field in risk, f"Missing risk field '{field}' in project {project.get('projectId')}"

    def test_risk_component_has_score_flagged_reason(self):
        data = get_json("/api/projects")
        for project in data["projects"]:
            for detector in ["cost", "delay", "expenditure", "duplicate"]:
                comp = project["risk"][detector]
                assert "score" in comp
                assert "flagged" in comp
                assert "reason" in comp


# ---------------------------------------------------------------------------
# GET /api/projects/{projectId} — single project
# ---------------------------------------------------------------------------

class TestGetProjectById:
    def test_returns_200_for_known_project(self):
        response = client.get("/api/projects/133166")
        assert response.status_code == 200

    def test_correct_project_returned(self):
        data = get_json("/api/projects/133166")
        assert data["projectId"] == "133166"
        assert "workName" in data

    def test_complete_risk_block_included(self):
        data = get_json("/api/projects/133166")
        assert "risk" in data
        assert "overallScore" in data["risk"]
        assert "level" in data["risk"]

    def test_similar_projects_included(self):
        data = get_json("/api/projects/133166")
        assert "similarProjects" in data
        assert isinstance(data["similarProjects"], list)

    def test_returns_404_for_nonexistent_project(self):
        response = client.get("/api/projects/does-not-exist")
        assert response.status_code == 404

    def test_404_response_has_detail(self):
        data = get_json("/api/projects/does-not-exist", expected_status=404)
        assert data["detail"] == "Project not found"


# ---------------------------------------------------------------------------
# GET /api/projects?risk=HIGH — risk filter
# ---------------------------------------------------------------------------

class TestRiskFilter:
    def test_high_risk_filter_returns_200(self):
        response = client.get("/api/projects?risk=HIGH")
        assert response.status_code == 200

    def test_high_risk_filter_returns_only_high(self):
        data = get_json("/api/projects?risk=HIGH")
        for project in data["projects"]:
            assert project["risk"]["level"].upper() == "HIGH"

    def test_medium_risk_filter_returns_only_medium(self):
        data = get_json("/api/projects?risk=MEDIUM")
        for project in data["projects"]:
            assert project["risk"]["level"].upper() == "MEDIUM"

    def test_low_risk_filter_returns_only_low(self):
        data = get_json("/api/projects?risk=LOW")
        for project in data["projects"]:
            assert project["risk"]["level"].upper() == "LOW"

    def test_total_matches_filtered_list_length(self):
        data = get_json("/api/projects?risk=HIGH")
        assert data["total"] == len(data["projects"])


# ---------------------------------------------------------------------------
# GET /api/projects?state=Karnataka — state filter
# ---------------------------------------------------------------------------

class TestStateFilter:
    def test_state_filter_returns_200(self):
        response = client.get("/api/projects?state=Karnataka")
        assert response.status_code == 200

    def test_state_filter_returns_only_karnataka(self):
        data = get_json("/api/projects?state=Karnataka")
        for project in data["projects"]:
            assert "karnataka" in project["state"].lower()

    def test_state_filter_total_matches_list(self):
        data = get_json("/api/projects?state=Karnataka")
        assert data["total"] == len(data["projects"])


# ---------------------------------------------------------------------------
# Combined risk + state filter
# ---------------------------------------------------------------------------

class TestCombinedFilter:
    def test_combined_filter_returns_200(self):
        response = client.get("/api/projects?risk=HIGH&state=Karnataka")
        assert response.status_code == 200

    def test_combined_filter_results_are_both_high_and_karnataka(self):
        data = get_json("/api/projects?risk=HIGH&state=Karnataka")
        for project in data["projects"]:
            assert project["risk"]["level"].upper() == "HIGH"
            assert "karnataka" in project["state"].lower()

    def test_combined_filter_total_matches_list(self):
        data = get_json("/api/projects?risk=HIGH&state=Karnataka")
        assert data["total"] == len(data["projects"])

    def test_impossible_combination_returns_empty(self):
        data = get_json("/api/projects?risk=LOW&state=DoesNotExistState")
        assert data["total"] == 0
        assert data["projects"] == []


# ---------------------------------------------------------------------------
# GET /api/alerts
# ---------------------------------------------------------------------------

class TestAlerts:
    def test_returns_200(self):
        response = client.get("/api/alerts")
        assert response.status_code == 200

    def test_response_has_total_and_alerts(self):
        data = get_json("/api/alerts")
        assert "total" in data
        assert "alerts" in data

    def test_total_matches_alerts_list_length(self):
        data = get_json("/api/alerts")
        assert data["total"] == len(data["alerts"])

    def test_each_alert_has_flagged_detectors(self):
        data = get_json("/api/alerts")
        for alert in data["alerts"]:
            assert "flaggedDetectors" in alert
            assert len(alert["flaggedDetectors"]) > 0

    def test_alert_fields_present(self):
        data = get_json("/api/alerts")
        required = ["projectId", "workName", "state", "constituency", "mpName",
                    "riskLevel", "overallScore", "flaggedDetectors"]
        for alert in data["alerts"]:
            for field in required:
                assert field in alert, f"Missing field '{field}' in alert {alert.get('projectId')}"

    def test_all_alerts_have_at_least_one_flagged_detector(self):
        data = get_json("/api/alerts")
        for alert in data["alerts"]:
            assert len(alert["flaggedDetectors"]) >= 1


# ---------------------------------------------------------------------------
# GET /api/statistics
# ---------------------------------------------------------------------------

class TestStatistics:
    def test_returns_200(self):
        response = client.get("/api/statistics")
        assert response.status_code == 200

    def test_response_has_required_fields(self):
        data = get_json("/api/statistics")
        for field in ["totalProjects", "highRisk", "mediumRisk", "lowRisk"]:
            assert field in data

    def test_statistics_dynamic_consistency(self):
        """Statistics must be consistent with the actual project list."""
        stats = get_json("/api/statistics")
        all_projects = get_json("/api/projects")

        assert stats["totalProjects"] == all_projects["total"]

        # Count risk levels from the full project list
        high = sum(1 for p in all_projects["projects"] if p["risk"]["level"].upper() == "HIGH")
        medium = sum(1 for p in all_projects["projects"] if p["risk"]["level"].upper() == "MEDIUM")
        low = sum(1 for p in all_projects["projects"] if p["risk"]["level"].upper() == "LOW")

        assert stats["highRisk"] == high
        assert stats["mediumRisk"] == medium
        assert stats["lowRisk"] == low

    def test_risk_counts_sum_to_total(self):
        data = get_json("/api/statistics")
        assert data["highRisk"] + data["mediumRisk"] + data["lowRisk"] == data["totalProjects"]
