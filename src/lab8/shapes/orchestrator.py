"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.handoff import HandoffError, make_handoff
from lab8.mock_llm import complete
from lab8.runtime import ToolRejected, run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import safe_dump
from lab8.shapes.workflow import finish_status, settle
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_refund_history", "compute_compensation"]


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    # Orchestrator reads the allowlisted claim view (never SELECT * on claims).
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        return finish_status(conn, SHAPE, claim_id, seed, "failed", 0, budget, trace, "unknown_claim")
    if not claim["order_id"]:
        return finish_status(conn, SHAPE, claim_id, seed, "needs_info", 0, budget, trace, "missing_order_id")

    complete(budget, seed=seed, purpose="plan", prompt=f"{claim_id}|delegate=check_applicable_policy")

    # 1. Typed handoff: allowlisted fields, read-only tools, no parent context in facts.
    try:
        handoff = make_handoff(
            request_id=f"REQ-{claim_id}",
            claim_id=claim_id,
            task="check_applicable_policy",
            facts={},
            allowed_tools=INVESTIGATOR_TOOLS,
        )
    except HandoffError as exc:
        return finish_status(conn, SHAPE, claim_id, seed, "failed", 0, budget, trace, f"handoff_rejected:{exc}")
    # 4. Trace the sanitized handoff only.
    trace.add("handoff", safe_dump(handoff))

    # 2. Investigators run with read tools only.
    try:
        investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    except ToolRejected as exc:
        return finish_status(conn, SHAPE, claim_id, seed, "failed", 0, budget, trace, f"tool_rejected:{exc}")
    complete(budget, seed=seed, purpose="investigate", prompt=f"{claim_id}|tools={','.join(INVESTIGATOR_TOOLS)}")

    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    if not order_view.get("visible"):
        trace.add("investigator", {"visible": False, "reason": order_view.get("reason")})
        return finish_status(conn, SHAPE, claim_id, seed, "escalated", 0, budget, trace, order_view.get("reason"))
    history = tools.get("lookup_refund_history") or {}
    trace.add(
        "investigator",
        {
            "lookup_order": safe_dump(order_view),
            "refunded_vnd": history.get("refunded_vnd"),
            "investigator_quote_vnd": (tools.get("compute_compensation") or {}).get("amount_vnd"),
        },
    )

    # 3. Orchestrator quotes in code from the investigator's order view, then calls the host.
    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order_view["order"])
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={quote_payload['amount_vnd']}")
    return settle(conn, SHAPE, claim_id, seed, quote_payload, budget, trace, crash_at=crash_at)
