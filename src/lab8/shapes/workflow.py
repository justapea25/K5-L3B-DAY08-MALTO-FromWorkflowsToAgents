"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"


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

    # 1. Claim view: allowlisted columns only (no parent_secret, no raw_headers).
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        trace.add("error", {"reason": "unknown_claim"})
        return finish_status(conn, SHAPE, claim_id, seed, "failed", 0, budget, trace, "unknown_claim")
    trace.add("claim", {"claim_id": claim_id, "has_order_id": bool(claim["order_id"])})

    # 2. Missing order_id -> needs_info. Never parse an order id out of the ticket text.
    if not claim["order_id"]:
        return finish_status(conn, SHAPE, claim_id, seed, "needs_info", 0, budget, trace, "missing_order_id")

    # 3. Order lookup scoped to the claim's principal.
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    if not order_view["visible"]:
        trace.add("order", {"visible": False, "reason": order_view["reason"]})
        return finish_status(conn, SHAPE, claim_id, seed, "escalated", 0, budget, trace, order_view["reason"])
    trace.add("order", safe_dump(order_view))

    # 4. Quote from the order row only. Ticket text is user data, not a source of facts.
    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order_view["order"])

    # 8. MockLLM only drafts the reply. It never sees the amount decision as input it can change.
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={quote_payload['amount_vnd']}")

    # 5–7. Hand the full quote to the host gate.
    return settle(conn, SHAPE, claim_id, seed, quote_payload, budget, trace, crash_at=crash_at)


# ---------------------------------------------------------------------------
# Shared by workflow, single and orchestrator. Kept in this file because the
# hidden grader only copies the three shape files from the group repo.
# ---------------------------------------------------------------------------


def finish_status(
    conn: sqlite3.Connection,
    shape: str,
    claim_id: str,
    seed: int,
    status: str,
    proposal: int,
    budget: Budget,
    trace: Trace,
    reason: str | None,
) -> RunResult:
    trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
    return finish(
        conn,
        shape=shape,
        claim_id=claim_id,
        seed=seed,
        status=status,
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=reason,
    )


def settle(
    conn: sqlite3.Connection,
    shape: str,
    claim_id: str,
    seed: int,
    quote_payload: dict[str, Any],
    budget: Budget,
    trace: Trace,
    *,
    crash_at: str | None,
) -> RunResult:
    """Map a code-computed quote to a host call and a RunResult.

    quote 0  -> denied, proposal 0, issue_refund NOT called.
    quote >0 -> issue_refund with the FULL quote (host caps per order and checks approval).
    """
    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", safe_dump(quote_payload))
    if proposal <= 0:
        return finish_status(conn, shape, claim_id, seed, "denied", 0, budget, trace, quote_payload.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        # Flush the trace so the crashed run is still auditable, then let the crash propagate.
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
    if outcome["ok"]:
        return finish_status(conn, shape, claim_id, seed, "resolved", proposal, budget, trace, None)
    status = "failed" if outcome["conflict"] else "denied"
    return finish_status(conn, shape, claim_id, seed, status, proposal, budget, trace, outcome["reason"])
