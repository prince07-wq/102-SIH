"""
routes/statistics.py
=====================
HTTP route handlers for alerts and statistics endpoints.

ARCHITECTURE NOTE
-----------------
Route functions handle ONLY HTTP concerns.  All data access and
aggregation logic is delegated to project_service.py.
"""

from fastapi import APIRouter

from app.schemas.project import AlertsResponse, StatisticsResponse
from app.services import project_service

router = APIRouter(tags=["statistics"])


@router.get("/api/alerts", response_model=AlertsResponse)
def get_alerts():
    """
    GET /api/alerts

    Return projects that require review — i.e. projects where at least one
    risk detector is flagged.

    This endpoint reuses the existing risk fields in each project record.
    It does NOT perform any new risk calculation or ML inference.
    """
    return project_service.get_alerts()


@router.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics():
    """
    GET /api/statistics

    Return aggregate counts calculated dynamically from the current dataset:

    - **totalProjects** : total number of records
    - **highRisk**      : projects with risk level HIGH
    - **mediumRisk**    : projects with risk level MEDIUM
    - **lowRisk**       : projects with risk level LOW

    Numbers are recalculated on every request; they are never hardcoded.
    """
    return project_service.get_statistics()
