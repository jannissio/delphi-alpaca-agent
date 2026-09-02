"""Tail state/audit.jsonl and print one line per notable event (for the operator's monitor).

Suppresses heartbeats/marks/snapshots, prints heartbeat messages only when they change, and
prints repeated NO_TRADE reasons at most once per minute. Exits never; stop with Ctrl-C.

    python scripts/watch_audit.py
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.core.config import STATE_DIR  # noqa: E402

ET = ZoneInfo("America/New_York")
PATH = STATE_DIR / "audit.jsonl"
QUIET = {"mark", "regime_snapshot", "chain", "vix1d_tercile", "event_vol"}


def fmt(r: dict) -> str | None:
    k = r["kind"]
    t = datetime.fromisoformat(r["ts"]).astimezone(ET).strftime("%H:%M:%S ET")
    if k in QUIET:
        return None
    if k in ("heartbeat", "no_trade"):
        return f"{t} {k}: {r.get('msg') or r.get('reason')}"
    if k == "gates":
        c = r.get("candidate", {})
        failed = [g["name"] for g in r.get("results", []) if not g["passed"]]
        return (f"{t} gates {'PASS' if r.get('passed') else 'REJECT ' + ','.join(failed)} | "
                f"{c.get('short_put')}/{c.get('short_call')} x{c.get('contracts')} credit {c.get('credit_mid')} maxloss {c.get('max_loss_total')}")
    if k == "llm_regime":
        d, m = r.get("decision") or {}, r.get("meta") or {}
        return f"{t} llm_regime {d.get('strategy_family')} veto={d.get('veto')} unanimous={m.get('unanimous')} H={m.get('entropy_bits', {}).get('strategy_family') if m.get('entropy_bits') else '-'}"
    if k == "llm_critic":
        d = r.get("decision") or {}
        return f"{t} llm_critic {d.get('verdict')}: {str(d.get('reason'))[:100]}"
    if k == "conformal_interval":
        s = r.get("session", {})
        return (f"{t} conformal_interval rule={s.get('rule')} k={round(s.get('k', 0), 3)} beta_t={round(s.get('beta_t', 0), 4)} "
                f"k_crc={round(s.get('k_crc', 0), 3)} alpha_t={round(s.get('alpha_t', 0), 4)} k_cov={round(s.get('k_cov', 0), 3)} n={s.get('n')} "
                f"impl_ref_usd={round(s.get('impl_ref_usd', 0), 2)} spot={s.get('spot_entry')}")
    if k == "conformal":
        l, cf = r.get("ledger", {}), r.get("counterfactual_fixed", {})
        return (f"{t} conformal credit/wing={l.get('q_mid', 0):.3f} beta*={l.get('beta_certified')} empirical_payout={l.get('beta_empirical', 0):.3f} P_mid={l.get('p_mid', 0):.3f} gap={l.get('gap', 0):+.3f} "
                f"margin={l.get('margin')} -> {'PASS' if l.get('passes') else 'REJECT'} | fixed rule gap={cf.get('gap')}")
    if k == "conformal_eod":
        c = r.get("record", {})
        return (f"{t} conformal_eod ratio={c.get('ratio', 0):.3f} k={c.get('k')} payout_ratio={c.get('loss', 0):.3f} "
                f"beta {c.get('beta_before', 0):.4f} -> {c.get('beta_after', 0):.4f} | err={c.get('err')} alpha {c.get('alpha_before', 0):.4f} -> {c.get('alpha_after', 0):.4f}")
    if k == "regime_model":
        return f"{t} regime_model p_inside={r.get('p_inside')} multiplier={r.get('multiplier')}"
    if k in ("order_submitted", "order_filled", "order_partial", "order_terminal", "order_walk_timeout",
             "order_submit_error", "order_price_rejected_by_collar"):
        return f"{t} {k} {r.get('tag','')} price={r.get('price')} signed={r.get('signed_limit')} qty={r.get('qty')} step={r.get('step')} status={r.get('status','')} err={str(r.get('error',''))[:120]}"
    if k == "position_opened":
        p = r.get("position", {})
        return f"{t} POSITION OPENED x{p.get('contracts')} credit {p.get('entry_credit')} maxloss {p.get('max_loss_total')} rung {r.get('fill_rung')} slippage {r.get('slippage_vs_mid_usd')}"
    if k == "position_closed":
        return f"{t} POSITION CLOSED {r.get('reason')} exit {r.get('exit_debit')} pnl {r.get('pnl')}"
    if k in ("flatten_start", "flatten_result", "flatten_failed", "flatten_deadline_reached", "flatten_skipped_no_quotes"):
        return f"{t} {k} {r.get('reason','')} {r.get('status','')} {r.get('close_natural','')}"
    if k in ("halt", "kill_switch", "kill_switch_seen", "recon_position_mismatch", "recon_order_mismatch", "cycle_error",
             "gate", "critic_reduce", "regime_model_error", "recon_order_error", "event_vol_error", "open_not_filled", "dry_run_would_open",
             "conformal_error"):
        return f"{t} !! {k}: {r.get('reason') or r.get('error') or r.get('problems') or r.get('result') or ''}"[:300]
    if k in ("agent_start", "agent_stop", "execute_start"):
        return f"{t} {k} {r.get('prices','')} {r.get('rationale','')[:120]}"
    return f"{t} {k}"


def main() -> None:
    pos = PATH.stat().st_size if PATH.exists() else 0
    last_hb = None
    last_nt: tuple[str, float] | None = None
    while True:
        if PATH.exists() and PATH.stat().st_size > pos:
            with open(PATH, encoding="utf-8") as f:
                f.seek(pos)
                chunk = f.read()
                pos = f.tell()
            for line in chunk.splitlines():
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                out = fmt(r)
                if out is None:
                    continue
                if r["kind"] == "heartbeat":
                    if r.get("msg") == last_hb:
                        continue
                    last_hb = r.get("msg")
                if r["kind"] == "no_trade":
                    key = str(r.get("reason"))[:80]
                    now = time.time()
                    if last_nt and last_nt[0] == key and now - last_nt[1] < 60:
                        continue
                    last_nt = (key, now)
                print(out, flush=True)
        time.sleep(2)


if __name__ == "__main__":
    main()
