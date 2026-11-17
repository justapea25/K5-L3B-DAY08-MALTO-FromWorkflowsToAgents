"""Group tests for durability and the trace security boundary, across all three group shapes.

Covers two must-pass conditions for whichever shape the group picks:
crash never creates more than one refund, and no secret/PII ever reaches the trace or result.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

GROUP_SHAPES = ["workflow", "single", "orchestrator"]
CRASH_POINTS = ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]
PII_FIELDS = ("phone", "address", "internal_note", "item_name")


def _store(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def _artifacts(result) -> str:
    """Trace plus every <run_id>* file next to it, the same set the grader scans."""
    trace_path = Path(result.trace_path)
    blobs = [path.read_text(encoding="utf-8") for path in trace_path.parent.glob(f"{result.run_id}*")]
    return "\n".join(blobs) + json.dumps(result.as_dict(), ensure_ascii=False)


@pytest.mark.parametrize("shape", GROUP_SHAPES)
@pytest.mark.parametrize("point", CRASH_POINTS)
def test_crash_then_resume_pays_exactly_once(tmp_path, shape, point):
    store = _store(tmp_path, f"{shape}-{point}.sqlite")
    with pytest.raises(InjectedCrash):
        SHAPES[shape]("C-001", seed=11, store_path=str(store), crash_at=point)
    result = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'").fetchone()["n"]
        assert count == 1
        assert int(get_refund(conn, "C-001")["amount_vnd"]) == 35000
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()
    assert result.status == "resolved"


@pytest.mark.parametrize("shape", GROUP_SHAPES)
def test_trace_has_no_secret_or_pii_on_any_public_claim(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-leak.sqlite")
    forbidden = ["CANARY_SECRET_", "CANARY_INTERNAL_", "parent_secret", "raw_headers", "Bearer "]
    for order in WORLD["orders"]:
        forbidden += [str(order[field]) for field in PII_FIELDS if order.get(field)]
    for claim in CLAIMS:
        result = SHAPES[shape](claim["claim_id"], seed=11, store_path=str(store))
        blob = _artifacts(result)
        leaked = [token for token in forbidden if token in blob]
        assert not leaked, f"{claim['claim_id']} leaked {leaked}"


@pytest.mark.parametrize("shape", GROUP_SHAPES)
def test_trace_run_id_matches_result(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-runid.sqlite")
    result = SHAPES[shape]("C-003", seed=22, store_path=str(store))
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id == f"R-{shape}-C-003-s22"
    assert isinstance(body["events"], list) and body["events"]
