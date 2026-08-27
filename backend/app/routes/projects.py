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

from app.schemas.project import ProjectListResponse, ProjectRecord
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    risk: Optional[str] = Query(
        default=None,
        description="Filter by risk level: LOW | MEDIUM | HIGH",
    ),
    state: Optional[str] = Query(
        default=None,
        description="Filter by state name (case-insensitive).",
    ),
):
    """
    GET /api/projects

    Return all project records.  Supports optional query-string filters:

    - **risk**  : LOW | MEDIUM | HIGH
    - **state** : state name (e.g. Karnataka)

    Both filters can be combined:  /api/projects?risk=HIGH&state=Karnataka
    """
    return project_service.get_all_projects(risk=risk, state=state)


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
