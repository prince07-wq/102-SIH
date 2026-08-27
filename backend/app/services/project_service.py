"""
services/project_service.py
============================
Data-access layer for MPLADS project records.

ARCHITECTURE NOTE
-----------------
Routes MUST NOT directly read projects.json.  All file I/O and data
filtering lives here so that this file can later be replaced by a real
processed MPLADS / ML-output source without changing any route or schema.

Current source  : mock/projects.json  (synthetic data)
Future source   : processed MPLADS data + anomaly/risk output (TBD)
"""

import json
import os
from typing import List, Optional

from app.schemas.project import (
    AlertRecord,
    AlertsResponse,
    ProjectListResponse,
    ProjectRecord,
    StatisticsResponse,
)

# ---------------------------------------------------------------------------
# Path to the mock data file — relative to this service file so it works
# regardless of where uvicorn is launched from.
# ---------------------------------------------------------------------------
_MOCK_PATH = os.path.join(
    os.path.dirname(__file__),   # …/app/services/
    "..",                        # …/app/
    "..",                        # …/backend/
    "mock",
    "projects.json",
)


def _load_all() -> List[ProjectRecord]:
    """
    Load and parse every record from the mock JSON file.

    Replace the body of this function (only) when switching to a real
    MPLADS data source.  The return type and callers stay the same.
    """
    with open(_MOCK_PATH, "r", encoding="utf-8") as fh:
        raw: list = json.load(fh)
    return [ProjectRecord(**item) for item in raw]


# ---------------------------------------------------------------------------
# Public service functions called by route handlers
# ---------------------------------------------------------------------------

def get_all_projects(
    risk: Optional[str] = None,
    state: Optional[str] = None,
) -> ProjectListResponse:
    """
    Return all projects, optionally filtered by risk level and/or state.

    Parameters
    ----------
    risk  : "LOW" | "MEDIUM" | "HIGH"  (case-insensitive)
    state : state name string           (case-insensitive partial match)
    """
    projects = _load_all()

    if risk:
        risk_upper = risk.upper()
        projects = [p for p in projects if p.risk.level.upper() == risk_upper]

    if state:
        state_lower = state.lower()
        projects = [p for p in projects if state_lower in p.state.lower()]

    return ProjectListResponse(total=len(projects), projects=projects)


def get_project_by_id(project_id: str) -> Optional[ProjectRecord]:
    """
    Return a single project by its projectId, or None if not found.
    """
    projects = _load_all()
    for project in projects:
        if project.projectId == project_id:
            return project
    return None


def get_alerts() -> AlertsResponse:
    """
    Return projects that require review.

    "Requires review" means at least one risk detector is flagged.
    This function reuses the existing risk data — it does NOT calculate
    new risk scores.
    """
    projects = _load_all()
    alert_list: List[AlertRecord] = []

    for project in projects:
        risk = project.risk
        flagged_detectors: List[str] = []

        if risk.cost.flagged:
            flagged_detectors.append("cost")
        if risk.delay.flagged:
            flagged_detectors.append("delay")
        if risk.expenditure.flagged:
            flagged_detectors.append("expenditure")
        if risk.duplicate.flagged:
            flagged_detectors.append("duplicate")

        if flagged_detectors:
            alert_list.append(
                AlertRecord(
                    projectId=project.projectId,
                    workName=project.workName,
                    state=project.state,
                    constituency=project.constituency,
                    mpName=project.mpName,
                    riskLevel=risk.level,
                    overallScore=risk.overallScore,
                    flaggedDetectors=flagged_detectors,
                )
            )

    return AlertsResponse(total=len(alert_list), alerts=alert_list)


def get_statistics() -> StatisticsResponse:
    """
    Return aggregate counts calculated dynamically from the current dataset.

    Numbers are never hardcoded — they are recalculated on every request so
    that they stay consistent when the data source is updated.
    """
    projects = _load_all()
    high = sum(1 for p in projects if p.risk.level.upper() == "HIGH")
    medium = sum(1 for p in projects if p.risk.level.upper() == "MEDIUM")
    low = sum(1 for p in projects if p.risk.level.upper() == "LOW")

    return StatisticsResponse(
        totalProjects=len(projects),
        highRisk=high,
        mediumRisk=medium,
        lowRisk=low,
    )
