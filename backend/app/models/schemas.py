from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):
    error: dict[str, str]


class RepositoryMeta(BaseModel):
    owner: str
    name: str
    ref: str | None = None


class ScanCreateRequest(BaseModel):
    repository_url: str
    ref: str | None = None


class ScanStatusResponse(BaseModel):
    scan_id: str
    status: str
    repository: RepositoryMeta


class CoverageResponse(BaseModel):
    files_discovered: int = 0
    files_analyzed: int = 0
    files_skipped: int = 0
    warnings: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    model_config = ConfigDict(extra="ignore")

    finding_id: str
    source_type: Literal["bandit", "ai_review", "combined"]
    rule_id: str | None = None
    title: str | None = None
    message: str | None = None
    severity: str | None = None
    priority: str | None = None
    confidence: str | None = None
    file_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    evidence: str | None = None
    rationale: str | None = None
    manual_review_required: bool = True


class ScanDetailResponse(BaseModel):
    scan_id: str
    status: str
    error_code: str | None = None
    error_message: str | None = None
    repository_url: str | None = None
    repository_name: str | None = None
    files_analyzed: int | None = None
    coverage: CoverageResponse = Field(default_factory=CoverageResponse)
    stages: dict[str, str] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)


class FixRequest(BaseModel):
    finding_id: str


class FixProposalResponse(BaseModel):
    proposal_id: str
    finding_id: str
    status: str = "proposed"
    explanation: str
    target_path: str
    diff: str
    review_notes: list[str] = Field(default_factory=list)


class RescanRequest(BaseModel):
    proposal_id: str
    finding_id: str | None = None
    patch: str | None = None


class VerificationResponse(BaseModel):
    verification_id: str
    proposal_id: str
    status: Literal["resolved", "still_detected", "unverified"]
    checks_run: list[str]
    evidence: str
    limitations: list[str] = Field(default_factory=list)


class ScanSummaryResponse(BaseModel):
    scan_id: str
    repository_url: str
    owner: str | None = None
    repository_name: str | None = None
    ref: str | None = None
    status: str
    error_code: str | None = None
    error_message: str | None = None
    findings_count: int = 0
    created_at: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
