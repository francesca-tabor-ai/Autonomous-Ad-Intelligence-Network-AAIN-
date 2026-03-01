from __future__ import annotations

from aain.core.blackboard import Blackboard


def test_read_write() -> None:
    bb = Blackboard("test-1")
    bb.write("agent_a", "key1", "value1")
    assert bb.read("key1") == "value1"
    assert bb.read("missing") is None
    assert bb.read("missing", "default") == "default"


def test_has() -> None:
    bb = Blackboard("test-2")
    assert not bb.has("key1")
    bb.write("agent_a", "key1", 42)
    assert bb.has("key1")


def test_snapshot() -> None:
    bb = Blackboard("test-3")
    bb.write("a", "x", 1)
    bb.write("b", "y", 2)
    snap = bb.snapshot()
    assert snap == {"x": 1, "y": 2}
    # Snapshot is a copy
    snap["z"] = 3
    assert not bb.has("z")


def test_audit_trail() -> None:
    bb = Blackboard("test-4")
    bb.write("agent_a", "k1", "v1")
    bb.write("agent_b", "k2", "v2")
    trail = bb.audit_trail
    assert len(trail) == 2
    assert trail[0] == ("agent_a", "k1", "v1")
    assert trail[1] == ("agent_b", "k2", "v2")
