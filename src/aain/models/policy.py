from __future__ import annotations

from pydantic import BaseModel, Field


class ComplianceViolation(BaseModel):
    rule_id: str
    rule_name: str
    severity: str = "warning"
    description: str = ""


class ComplianceResult(BaseModel):
    passed: bool = True
    violations: list[ComplianceViolation] = Field(default_factory=list)
    checked_rules: int = 0


class BrandSafetyScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0, default=1.0)
    flagged_categories: list[str] = Field(default_factory=list)
    blocked: bool = False


class TrustAssessment(BaseModel):
    approved: bool = True
    action: str = "serve"  # serve, downgrade, block
    reasoning: str = ""
    fatigue_override: bool = False


class AuditEntry(BaseModel):
    entry_id: str
    timestamp: float
    action: str
    agent_id: str
    details: dict = Field(default_factory=dict)
    correlation_id: str = ""
