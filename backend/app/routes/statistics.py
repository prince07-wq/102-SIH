"""
routes/statistics.py
=====================
HTTP route handlers for alerts and statistics endpoints.

ARCHITECTURE NOTE
-----------------
Route functions handle ONLY HTTP concerns.  All data access and
aggregation logic is delegated to project_service.py.
"""

from fastapi import APIRouter, Query

from app.schemas.project import AlertsResponse, StatisticsResponse
from app.services import project_service

router = APIRouter(tags=["statistics"])


@router.get("/api/alerts", response_model=AlertsResponse)
def get_alerts(
    page: int = Query(default=1, ge=1, description="One-based page number."),
    page_size: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Alerts per page (maximum 100).",
    ),
):
    """
    GET /api/alerts

    Return projects that require review — i.e. projects where at least one
    risk detector is flagged.

    This endpoint reuses the existing risk fields in each project record.
    It does NOT perform any new risk calculation or ML inference.
    """
    return project_service.get_alerts(page=page, page_size=page_size)


@router.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics():
    """
    GET /api/statistics

    Return aggregate counts calculated dynamically from the current dataset:

    - **totalProjects** : total number of records
    - **highRisk**      : projects with risk level HIGH
    - **mediumRisk**    : projects with risk level MODERATE (legacy field name)
    - **lowRisk**       : projects with risk level LOW
    - **criticalRisk**  : projects with risk level CRITICAL

    Numbers are derived from the processed dataset and cached per server process.
    """
    return project_service.get_statistics()
