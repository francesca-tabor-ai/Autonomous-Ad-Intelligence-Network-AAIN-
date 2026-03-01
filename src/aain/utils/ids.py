from __future__ import annotations

import uuid


def generate_id() -> str:
    return uuid.uuid4().hex


def generate_correlation_id() -> str:
    return f"corr-{uuid.uuid4().hex[:16]}"


def generate_event_id() -> str:
    return f"evt-{uuid.uuid4().hex[:16]}"
