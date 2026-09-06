"""
schemas/project.py
==================
Pydantic response models for the MPLADS Risk Intelligence System.

These models define the API contract between the backend and the React
frontend.  Field names and types MUST NOT change without a coordinated
frontend update.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Risk sub-components
# ---------------------------------------------------------------------------

class RiskComponent(BaseModel):
    """One detector inside the overall risk assessment."""

    score: float
    flagged: bool
    reason: str


class RiskDetail(BaseModel):
    """Full risk breakdown attached to every project record."""

    overallScore: float
    level: str           # "LOW" | "MODERATE" | "HIGH" | "CRITICAL"
    flagCount: int
    baseScore: float
    strongestDetector: str
    multiSignalBonus: int
    scoreCapped: bool
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
    sanctionDate: Optional[str] = None
    dateDifferenceDays: Optional[int] = None
    similarity: Optional[float] = None


class VendorRecord(BaseModel):
    """Vendor reference preserved from the expenditure aggregates."""

    vendorId: Optional[str] = None
    vendorName: Optional[str] = None


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
    activityName: Optional[str]
    description: Optional[str]
    category: str
    state: str
    constituency: str
    mpName: str
    authority: str
    recommendationDate: str   # ISO-8601 date string, e.g. "2024-07-08"
    sanctionDate: str         # ISO-8601 date string
    sanctionAmount: float
    workStage: str
    vendorName: Optional[str]
    totalDisbursed: float
    lastExpenditureDate: Optional[str]  # ISO-8601 date string
    tenure: Optional[str]
    houseOfParliament: Optional[int]
    hasExpenditure: bool
    expenditureRecordCount: int
    uniqueVendorCount: int
    firstExpenditureDate: Optional[str]
    vendors: List[VendorRecord]
    workIds: List[str]
    officialWorkIds: List[int]
    hasOfficialAttachment: bool
    risk: RiskDetail
    similarProjects: List[SimilarProject]


# ---------------------------------------------------------------------------
# On-demand official evidence
# ---------------------------------------------------------------------------

EvidenceType = Literal[
    "PHOTO_GPS",
    "PHOTO_ONLY",
    "DOCUMENT_ONLY",
    "NO_ATTACHMENT",
    "PROCESSING_FAILED",
]


class EvidencePhoto(BaseModel):
    """One safely served photo extracted from an official attachment."""

    url: str
    attachment_id: str
    source_page: Optional[int] = None


class EvidenceAttachment(BaseModel):
    """Normalized public metadata for one downloaded official attachment."""

    attachment_id: str
    original_file_name: Optional[str] = None
    content_type: Optional[str] = None
    evidence_type: EvidenceType
    original_url: Optional[str] = None
    photos: List[EvidencePhoto]
    processing_error: Optional[str] = None


class ProjectEvidenceResponse(BaseModel):
    """On-demand evidence result for one project."""

    status: EvidenceType
    attachments: List[EvidenceAttachment]
    has_project_photo: bool
    photos: List[EvidencePhoto]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_text: Optional[str] = None
    timestamp: Optional[str] = None
    original_file_name: Optional[str] = None
    evidence_type: EvidenceType
    cached: bool


# ---------------------------------------------------------------------------
# Collection response
# ---------------------------------------------------------------------------

class ProjectListResponse(BaseModel):
    """Wrapper returned by list endpoints so the contract stays extensible."""

    total: int
    page: int
    pageSize: int
    totalPages: int
    projects: List[ProjectRecord]


class ProjectFilterOptions(BaseModel):
    """Distinct values used by project-list filters."""

    states: List[str]
    categories: List[str]
    riskLevels: List[str]


class RiskLevelCounts(BaseModel):
    """Project counts for every Combined Risk V1 level."""

    low: int
    moderate: int
    high: int
    critical: int


class FlaggedComponentCounts(BaseModel):
    """Counts of detector-provided flags by component."""

    cost: int
    delay: int
    expenditure: int
    duplicate: int


class StateAggregate(BaseModel):
    """Filtered project count and average overall risk for one state."""

    state: str
    projectCount: int
    averageRisk: float


class ProjectAggregatesResponse(BaseModel):
    """Analytics calculated across the complete filtered project set."""

    totalProjects: int
    totalSanctionAmount: float
    totalExpenditure: float
    riskLevelCounts: RiskLevelCounts
    requiresReviewCount: int
    stateAggregates: List[StateAggregate]
    flaggedComponentCounts: FlaggedComponentCounts


# ---------------------------------------------------------------------------
# Statistics response
# ---------------------------------------------------------------------------

class StatisticsResponse(BaseModel):
    """Aggregate counts calculated dynamically from the current data."""

    totalProjects: int
    highRisk: int
    mediumRisk: int
    lowRisk: int
    criticalRisk: int


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
    overallScore: float
    flaggedDetectors: List[str]


class AlertsResponse(BaseModel):
    total: int
    page: int
    pageSize: int
    totalPages: int
    alerts: List[AlertRecord]
