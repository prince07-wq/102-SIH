"""
routes/projects.py
==================
HTTP route handlers for project-related endpoints.

ARCHITECTURE NOTE
-----------------
Route functions handle ONLY HTTP concerns (request parameters, status codes,
response types).  All data access and filtering is delegated to
project_service.py.  This layer does NOT read projects.json directly.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.schemas.project import (
    ProjectAggregatesResponse,
    ProjectFilterOptions,
    ProjectListResponse,
    ProjectRecord,
)
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    risk: Optional[str] = Query(
        default=None,
        description=(
            "Filter by risk level: LOW | MODERATE | HIGH | CRITICAL. "
            "MEDIUM remains accepted as an alias for MODERATE."
        ),
    ),
    state: Optional[str] = Query(
        default=None,
        description="Filter by state name (case-insensitive).",
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter by exact work category (case-insensitive).",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search project ID, work text, location, MP, or vendor.",
    ),
    page: int = Query(default=1, ge=1, description="One-based page number."),
    page_size: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Projects per page (maximum 100).",
    ),
):
    """
    GET /api/projects

    Return a page of project records. Supports optional query-string filters:

    - **risk**  : LOW | MODERATE | HIGH | CRITICAL (MEDIUM aliases MODERATE)
    - **state** : state name (e.g. Karnataka)

    Filters and pagination can be combined:
    /api/projects?risk=HIGH&state=Karnataka&page=1&page_size=50
    """
    return project_service.get_all_projects(
        risk=risk,
        state=state,
        category=category,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get("/options", response_model=ProjectFilterOptions)
def get_project_filter_options():
    """Returns real state, category, and risk-level filter values."""
    return project_service.get_project_filter_options()


@router.get("/aggregates", response_model=ProjectAggregatesResponse)
def get_project_aggregates(
    risk: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """Returns analytics across the complete filtered project result set."""
    return project_service.get_project_aggregates(
        risk=risk,
        state=state,
        category=category,
        search=search,
    )


@router.get("/export")
def export_projects(
    risk: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """Streams all projects matching the same list and aggregate filters."""
    rows = project_service.iter_project_export(
        risk=risk,
        state=state,
        category=category,
        search=search,
    )
    return StreamingResponse(
        rows,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                'attachment; filename="mplads-filtered-projects.csv"'
            )
        },
    )


@router.get("/{project_id}", response_model=ProjectRecord)
def get_project(project_id: str):
    """
    GET /api/projects/{projectId}

    Return a single project by its projectId.
    Returns HTTP 404 with `{"detail": "Project not found"}` if not found.
    """
    project = project_service.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
