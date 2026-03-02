from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.policy.supervisor import PolicyClusterSupervisor
from aain.models.intent import IntentSignal, IntentType, UserState
from aain.models.policy import ComplianceResult, BrandSafetyScore, TrustAssessment


@pytest.fixture
def cluster() -> PolicyClusterSupervisor:
    return PolicyClusterSupervisor(AsyncEventBus())


def _event(bb: Blackboard) -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "policy"},
    )


async def test_passes_safe_content(cluster: PolicyClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM for startups",
        intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(session_id="s1", ad_fatigue_score=0.1))

    await cluster.run_cluster(_event(bb), bb)

    compliance: ComplianceResult = bb.read("compliance_result")
    assert compliance.passed is True

    safety: BrandSafetyScore = bb.read("brand_safety_score")
    assert safety.blocked is False

    trust: TrustAssessment = bb.read("trust_assessment")
    assert trust.approved is True
    assert not bb.has("pipeline_veto")


async def test_vetoes_regulated_category(cluster: PolicyClusterSupervisor) -> None:
    bb = Blackboard("test-2")
    bb.write("test", "parsed_intent", IntentSignal(
        query="buy cheap tobacco online",
        intent_type=IntentType.TRANSACTIONAL,
        confidence=0.9, categories=["tobacco"],
    ))
    bb.write("test", "user_state", UserState(session_id="s1"))

    await cluster.run_cluster(_event(bb), bb)

    compliance: ComplianceResult = bb.read("compliance_result")
    assert compliance.passed is False
    assert bb.read("pipeline_veto") is True


async def test_blocks_unsafe_content(cluster: PolicyClusterSupervisor) -> None:
    bb = Blackboard("test-3")
    bb.write("test", "parsed_intent", IntentSignal(
        query="hack exploit attack systems",
        intent_type=IntentType.INFORMATIONAL,
        confidence=0.5, categories=[],
    ))
    bb.write("test", "user_state", UserState(session_id="s1"))

    await cluster.run_cluster(_event(bb), bb)

    safety: BrandSafetyScore = bb.read("brand_safety_score")
    assert safety.score < 0.5
    assert len(safety.flagged_categories) > 0


async def test_trust_guardian_blocks_high_fatigue(cluster: PolicyClusterSupervisor) -> None:
    bb = Blackboard("test-4")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM", intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(
        session_id="s1", ad_fatigue_score=0.9, ads_shown_count=12,
    ))

    await cluster.run_cluster(_event(bb), bb)

    trust: TrustAssessment = bb.read("trust_assessment")
    assert trust.action == "block"
    assert bb.read("pipeline_veto") is True


async def test_trust_guardian_downgrades_moderate_fatigue(cluster: PolicyClusterSupervisor) -> None:
    bb = Blackboard("test-5")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM", intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(
        session_id="s1", ad_fatigue_score=0.6, ads_shown_count=5,
    ))

    await cluster.run_cluster(_event(bb), bb)

    trust: TrustAssessment = bb.read("trust_assessment")
    assert trust.action == "downgrade"
    assert trust.approved is True


async def test_opt_out_user_blocked(cluster: PolicyClusterSupervisor) -> None:
    bb = Blackboard("test-6")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM", intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(session_id="s1", opt_out=True))

    await cluster.run_cluster(_event(bb), bb)

    trust: TrustAssessment = bb.read("trust_assessment")
    assert trust.action == "block"
    assert bb.read("pipeline_veto") is True
