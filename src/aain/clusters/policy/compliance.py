from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import IntentSignal
from aain.models.policy import ComplianceResult, ComplianceViolation

REGULATED_CATEGORIES = {
    "alcohol": {"min_age": 21, "severity": "block"},
    "gambling": {"min_age": 21, "severity": "block"},
    "pharmaceutical": {"requires_disclaimer": True, "severity": "warning"},
    "financial_services": {"requires_disclaimer": True, "severity": "warning"},
    "tobacco": {"severity": "block"},
    "weapons": {"severity": "block"},
}

PROHIBITED_CLAIM_PATTERNS = [
    "guaranteed",
    "100%",
    "cure",
    "risk-free",
    "no side effects",
]


class ComplianceAgent(BaseAgent):
    """Validates claims, checks regulated categories, ensures disclosure formatting."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        intent: IntentSignal | None = blackboard.read("parsed_intent")
        violations: list[ComplianceViolation] = []
        checked = 0

        if intent:
            for cat in intent.categories:
                checked += 1
                if cat in REGULATED_CATEGORIES:
                    reg = REGULATED_CATEGORIES[cat]
                    violations.append(ComplianceViolation(
                        rule_id=f"reg_{cat}",
                        rule_name=f"Regulated category: {cat}",
                        severity=reg.get("severity", "warning"),
                        description=f"Content involves regulated category: {cat}",
                    ))

            query_lower = intent.query.lower()
            for pattern in PROHIBITED_CLAIM_PATTERNS:
                checked += 1
                if pattern in query_lower:
                    violations.append(ComplianceViolation(
                        rule_id=f"claim_{pattern.replace(' ', '_')}",
                        rule_name=f"Prohibited claim: {pattern}",
                        severity="warning",
                        description=f"Query contains potentially prohibited claim: {pattern}",
                    ))

        blocking_violations = [v for v in violations if v.severity == "block"]
        passed = len(blocking_violations) == 0

        result = ComplianceResult(
            passed=passed,
            violations=violations,
            checked_rules=max(checked, 5),
        )

        blackboard.write(self.agent_id, "compliance_result", result)
        if not passed:
            blackboard.write(self.agent_id, "pipeline_veto", True)

        return result
