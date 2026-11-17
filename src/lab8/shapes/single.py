"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.mock_llm import complete
from lab8.runtime import ToolRejected, run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import safe_dump
from lab8.shapes.workflow import finish_status, settle
from lab8.tools import compute_compensation, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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
    memory: dict[str, Any] = {}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        """The 'model'. One MockLLM call per step; it may only pick read tools.

        It keeps its own scratchpad (memory) because run_react only shows the last
        tool result. The prompt is the tool name, never raw ticket text or rows.
        """
        last_tool = observation.get("last_tool")
        if last_tool:
            memory[last_tool] = observation.get("last_result")
            trace.add("observe", {"tool": last_tool})
        complete(budget, seed=seed, purpose="react", prompt=f"{claim_id}|after={last_tool or 'start'}")

        claim = memory.get("get_claim_view")
        if claim is None:
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
        if not claim.get("found"):
            return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}

        scope = {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
        order_view = memory.get("lookup_order")
        if order_view is None:
            return {"tool": "lookup_order", "args": scope}
        if not order_view.get("visible"):
            return {"final": {"status": "escalated", "error_reason": order_view.get("reason")}}

        if "lookup_refund_history" not in memory:
            return {"tool": "lookup_refund_history", "args": scope}
        if "compute_compensation" not in memory:
            return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
        return {"final": {"status": "quote_ready"}}

    try:
        loop = run_react(conn, budget, observation={"claim_id": claim_id}, decide=decide, max_steps=MAX_STEPS)
    except ToolRejected as exc:
        return finish_status(conn, SHAPE, claim_id, seed, "failed", 0, budget, trace, f"tool_rejected:{exc}")

    final = loop["final"]
    trace.add("react_stop", {"stopped": loop["stopped"], "final_status": final.get("status")})
    status = final.get("status")
    if status in ("failed", "needs_info", "escalated"):
        return finish_status(conn, SHAPE, claim_id, seed, status, 0, budget, trace, final.get("error_reason"))

    # After the loop the model is out of the picture. Code re-quotes from the
    # allowlisted order view returned by lookup_order, not from any model output.
    order_view = memory.get("lookup_order") or {}
    if not order_view.get("visible"):
        return finish_status(conn, SHAPE, claim_id, seed, "failed", 0, budget, trace, "no_order_view")
    trace.add("order", safe_dump(order_view))
    history = memory.get("lookup_refund_history") or {}
    trace.add("refund_history", {"refunded_vnd": history.get("refunded_vnd"), "refund_count": history.get("refund_count")})

    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order_view["order"])
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={quote_payload['amount_vnd']}")
    # Full quote goes to the host; the history above is informational only.
    return settle(conn, SHAPE, claim_id, seed, quote_payload, budget, trace, crash_at=crash_at)
