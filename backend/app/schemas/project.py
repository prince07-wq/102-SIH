"""
schemas/project.py
==================
Pydantic response models for the MPLADS Risk Intelligence System.

These models define the API contract between the backend and the React
frontend.  Field names and types MUST NOT change without a coordinated
frontend update.
"""

from typing import List, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Risk sub-components
# ---------------------------------------------------------------------------

class RiskComponent(BaseModel):
    """One detector inside the overall risk assessment."""

    score: int
    flagged: bool
    reason: str


class RiskDetail(BaseModel):
    """Full risk breakdown attached to every project record."""

    overallScore: int
    level: str           # "LOW" | "MEDIUM" | "HIGH"
    cost: RiskComponent
    delay: RiskComponent
    expenditure: RiskComponent
    duplicate: RiskComponent


# ---------------------------------------------------------------------------
# Similar projects (lightweight reference)
# ---------------------------------------------------------------------------

class SimilarProject(BaseModel):
    projectId: str
    workName: str
    sanctionAmount: float
    similarity: float


# ---------------------------------------------------------------------------
# Main Project Risk Record
# ---------------------------------------------------------------------------

class ProjectRecord(BaseModel):
    """
    The canonical Project Risk Record.

    This schema is the single source of truth for the frontend API contract.
    Do NOT add, remove, or rename fields here without updating the frontend.
    """

    projectId: str
    workName: str
    description: str
    category: str
    state: str
    constituency: str
    mpName: str
    authority: str
    recommendationDate: str   # ISO-8601 date string, e.g. "2024-07-08"
    sanctionDate: str         # ISO-8601 date string
    sanctionAmount: float
    workStage: str
    vendorName: str
    totalDisbursed: float
    lastExpenditureDate: str  # ISO-8601 date string
    risk: RiskDetail
    similarProjects: List[SimilarProject]


# ---------------------------------------------------------------------------
# Collection response
# ---------------------------------------------------------------------------

class ProjectListResponse(BaseModel):
    """Wrapper returned by list endpoints so the contract stays extensible."""

    total: int
    projects: List[ProjectRecord]


# ---------------------------------------------------------------------------
# Statistics response
# ---------------------------------------------------------------------------

class StatisticsResponse(BaseModel):
    """Aggregate counts calculated dynamically from the current data."""

    totalProjects: int
    highRisk: int
    mediumRisk: int
    lowRisk: int


# ---------------------------------------------------------------------------
# Alerts response
# ---------------------------------------------------------------------------

class AlertRecord(BaseModel):
    """
    Lightweight alert entry derived from the existing ProjectRecord.

    No new risk calculation is performed — this reuses risk.level and
    risk.overallScore already present in the project record.
    """

    projectId: str
    workName: str
    state: str
    constituency: str
    mpName: str
    riskLevel: str
    overallScore: int
    flaggedDetectors: List[str]


class AlertsResponse(BaseModel):
    total: int
    alerts: List[AlertRecord]
