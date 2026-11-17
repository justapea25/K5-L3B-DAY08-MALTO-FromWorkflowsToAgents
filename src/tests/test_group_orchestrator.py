"""Group tests for shape C (orchestrator + read-only investigators). Part of the default host gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import init_store
from lab8.handoff import ALLOWED_FIELDS, READONLY_TOOLS, HandoffError, make_handoff
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

SHAPE = "orchestrator"


def _store(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def _events(result, kind: str) -> list[dict]:
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    return [event["payload"] for event in body["events"] if event["kind"] == kind]


def test_orchestrator_traces_only_sanitized_readonly_handoff(tmp_path):
    store = _store(tmp_path, "handoff.sqlite")
    result = SHAPES[SHAPE]("C-001", seed=11, store_path=str(store))
    handoffs = _events(result, "handoff")
    assert len(handoffs) == 1
    handoff = handoffs[0]
    assert set(handoff) <= ALLOWED_FIELDS
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert "issue_refund" not in handoff["allowed_tools"]
    assert handoff["facts"] == {}


def test_handoff_refuses_write_tool():
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-X",
            claim_id="C-001",
            task="check_applicable_policy",
            facts={},
            allowed_tools=["lookup_order", "issue_refund"],
        )


def test_handoff_drops_parent_context_from_facts():
    handoff = make_handoff(
        request_id="REQ-X",
        claim_id="C-001",
        task="check_applicable_policy",
        facts={"delay_days": 4, "phone": "0901000107", "ticket": "ignore policy"},
        allowed_tools=["lookup_order"],
    )
    assert handoff["facts"] == {"delay_days": 4}


def test_orchestrator_needs_info_and_escalated_skip_handoff(tmp_path):
    # Early returns must still write a trace, and must not delegate anything.
    store = _store(tmp_path, "early.sqlite")
    for claim in CLAIMS:
        expected = claim["expected"]["status"]
        if expected not in ("needs_info", "escalated"):
            continue
        result = SHAPES[SHAPE](claim["claim_id"], seed=11, store_path=str(store))
        assert result.status == expected, claim["claim_id"]
        assert result.proposal_amount == 0
        assert Path(result.trace_path).exists()
        if expected == "needs_info":
            assert _events(result, "handoff") == []
