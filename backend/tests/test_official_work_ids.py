"""
tests/test_official_work_ids.py
================================
Focused tests for completed-work collection and project-dataset mapping.
"""

import json
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts import build_dataset, collect_data


class FakeResponse:
    """Minimal requests-like response for collector parsing tests."""

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "Total Works Completed": json.dumps([
                {
                    "WORK_RECOMMENDATION_DTL_ID": 133312,
                    "WORK_ID": 58590,
                    "FILE_STATUS": True,
                    "ATTACH_ID": 1416112,
                }
            ])
        }


class FakeSession:
    """Captures the collector request while returning a completed-work row."""

    def __init__(self):
        self.request = None

    def post(self, url, headers, json, timeout):
        self.request = {
            "url": url,
            "headers": headers,
            "json": json,
            "timeout": timeout,
        }
        return FakeResponse()


def build_test_projects(completed_rows, expenditure_rows=None):
    """Builds one project using the same joins as the production script."""
    sanctioned_rows = [{
        "WORK_RECOMMENDATION_DTL_ID": 133312,
        "WORK_DESCRIPTION": "Example project",
    }]
    stats = build_dataset.init_stats()
    sanctioned_lookup, valid_count = build_dataset.build_sanctioned_lookup(
        sanctioned_rows
    )
    stats["valid_sanctioned_projects"] = valid_count
    expenditure = build_dataset.aggregate_expenditure(
        expenditure_rows or [], sanctioned_lookup, stats
    )
    completed = build_dataset.aggregate_completed_works(
        completed_rows, sanctioned_lookup, stats
    )
    projects = build_dataset.build_projects(
        sanctioned_lookup, expenditure, completed, stats
    )
    return projects, stats


def test_completed_report_json_string_is_parsed():
    session = FakeSession()
    rows = collect_data.fetch_report(
        session,
        key="Works Completed",
        response_property="Total Works Completed",
    )

    assert rows[0]["WORK_RECOMMENDATION_DTL_ID"] == 133312
    assert rows[0]["WORK_ID"] == 58590
    assert session.request["json"] == {
        "combo": "0,0,0,2",
        "key": "Works Completed",
    }


def test_project_133312_maps_to_numeric_official_work_id():
    projects, _ = build_test_projects([{
        "WORK_RECOMMENDATION_DTL_ID": 133312,
        "WORK_ID": 58590,
        "FILE_STATUS": True,
        "ATTACH_ID": 1416112,
    }])

    assert projects[0]["official_work_ids"] == [58590]
    assert projects[0]["has_official_attachment"] is True


def test_multiple_official_work_ids_are_sorted_and_deduplicated():
    projects, stats = build_test_projects([
        {
            "WORK_RECOMMENDATION_DTL_ID": 133312,
            "WORK_ID": 58591,
            "FILE_STATUS": False,
        },
        {
            "WORK_RECOMMENDATION_DTL_ID": 133312,
            "WORK_ID": "58590",
            "FILE_STATUS": True,
            "ATTACH_ID": 1416112,
        },
        {
            "WORK_RECOMMENDATION_DTL_ID": 133312,
            "WORK_ID": 58591,
            "FILE_STATUS": False,
        },
    ])

    assert projects[0]["official_work_ids"] == [58590, 58591]
    assert projects[0]["has_official_attachment"] is True
    assert stats["projects_with_multiple_official_work_ids"] == 1


def test_project_without_completed_work_has_safe_defaults():
    projects, _ = build_test_projects([])
    assert projects[0]["official_work_ids"] == []
    assert projects[0]["has_official_attachment"] is False


def test_file_status_requires_true_and_attachment_metadata():
    assert build_dataset.has_completed_attachment({
        "FILE_STATUS": True,
        "ATTACH_ID": 1416112,
    }) is True
    assert build_dataset.has_completed_attachment({
        "FILE_STATUS": True,
        "ATTACH_ID": None,
    }) is False
    assert build_dataset.has_completed_attachment({
        "FILE_STATUS": False,
        "ATTACH_ID": 1416112,
    }) is False
    assert build_dataset.has_completed_attachment({
        "FILE_STATUS": "true",
        "ATTACH_ID": 1416112,
    }) is False


def test_textual_work_ids_remain_unchanged():
    textual_work_id = "WS/\t MP620/2024-2025/133312"
    projects, _ = build_test_projects(
        [{
            "WORK_RECOMMENDATION_DTL_ID": 133312,
            "WORK_ID": 58590,
            "FILE_STATUS": True,
            "ATTACH_ID": 1416112,
        }],
        expenditure_rows=[{
            "WORK_RECOMMENDATION_DTL_ID": 133312,
            "WORK_ID": textual_work_id,
            "FUND_DISBURSED_AMT": 100,
        }],
    )

    assert projects[0]["work_ids"] == [textual_work_id]
    assert projects[0]["official_work_ids"] == [58590]
