from __future__ import annotations

from enum import Enum


class AgentState(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class EventType(str, Enum):
    INTENT = "intent"
    AUCTION = "auction"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    USER_FEEDBACK = "user_feedback"
    AGENT_HEARTBEAT = "agent_heartbeat"
    CLUSTER_RESULT = "cluster_result"
    PIPELINE_STAGE = "pipeline_stage"
    ECONOMY_TRANSACTION = "economy_transaction"
    OVERRIDE = "override"
    REWARD_SIGNAL = "reward_signal"


class ClusterID(str, Enum):
    INTENT = "intent"
    ADVERTISER = "advertiser"
    CREATIVE = "creative"
    ECONOMIC = "economic"
    PLACEMENT = "placement"
    POLICY = "policy"
    LEARNING = "learning"
