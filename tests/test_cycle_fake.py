"""End-to-end cycle test with fake broker, fake data and fake LLM providers.

Exercises agent.main.Agent.cycle() inside the Wednesday 10:00-11:00 ET window: regime votes,
candidate, sizing, gates, critic, order walker (fills at the natural rung), book persistence,
then a take-profit close on the next cycle. No network, no real keys needed beyond .env shape.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

import agent.main as main_mod
from agent.core.models import OptionQuote
from agent.llm.provider import LLMResult
from tests.test_core import synthetic_chain

ET = ZoneInfo("America/New_York")
TODAY = date(2026, 9, 2)


class FakeClock:
    """Patched into agent.main.datetime so the loop believes it is 10:20 ET on Wednesday."""
    current = datetime(2026, 9, 2, 10, 20, tzinfo=ET).astimezone(timezone.utc)

    @classmethod
    def now(cls, tz=None):
        return cls.current.astimezone(tz) if tz else cls.current

    @staticmethod
    def fromisoformat(s):
        return datetime.fromisoformat(s)

    @staticmethod
    def combine(*a, **k):
        return datetime.combine(*a, **k)

    min = datetime.min


class FakeTrading:
    def __init__(self):
        self.orders: dict[str, SimpleNamespace] = {}
        self.n = 0
        self.fill_at_rung = None    # set to a price to fill only at that price
        self.fill_at_step = None    # or: fill only the n-th submitted order (0-based)

    def submit_order(self, req):
        self.n += 1
        oid = f"ord{self.n}"
        px = abs(float(req.limit_price))
        self.last_signed_limit = float(req.limit_price)
        fill = (self.fill_at_rung is not None and abs(px - self.fill_at_rung) < 1e-9) or \
               (self.fill_at_step is not None and self.n - 1 == self.fill_at_step)
        o = SimpleNamespace(id=oid, status="filled" if fill else "new", filled_qty=str(req.qty) if fill else "0",
                            filled_avg_price=str(px) if fill else None, client_order_id=req.client_order_id,
                            legs=req.legs, qty=req.qty)
        self.orders[oid] = o
        return o

    def get_order_by_id(self, oid):
        return self.orders[oid]

    def cancel_order_by_id(self, oid):
        if self.orders[oid].status != "filled":
            self.orders[oid].status = "canceled"

    def get_orders(self, *a, **k):
        return list(self.orders.values())


class FakeData:
    def __init__(self, chain: list[OptionQuote], trading: FakeTrading):
        self.trading = trading
        self._chain = chain
        self._positions: list[dict] = []
        self.spot = 650.0

    def account(self):
        return {"id": "x", "account_number": "PA", "status": "ACTIVE", "equity": 100000.0, "cash": 100000.0,
                "buying_power": 200000.0, "options_buying_power": 100000.0, "options_approved_level": 3,
                "options_trading_level": 3, "last_equity": 100000.0}

    def clock(self):
        return {"is_open": True}

    def positions(self):
        return self._positions

    def orders_today(self):
        return self.trading.get_orders()

    def underlying_quote(self, symbol):
        from agent.core.models import UnderlyingQuote
        return UnderlyingQuote(symbol, self.spot - 0.01, self.spot + 0.01, FakeClock.now(timezone.utc))

    def intraday_closes(self, symbol, minutes=5):
        return [649.5, 649.8, 650.1, 649.9, 650.2, 650.0, 650.1, 649.9]

    def _fresh(self, quotes):
        """Real feeds re-stamp every snapshot; the fake does the same so staleness is not an artefact."""
        ts = FakeClock.now(timezone.utc)
        return [OptionQuote(**{**q.__dict__, "quote_ts": ts}) for q in quotes]

    def chain(self, underlying, expiry, spot, width_pct=0.03):
        return self._fresh(self._chain)

    requote_scale = 1.0   # < 1: every option price has decayed since the decision chain was fetched

    def snapshots(self, symbols):
        out = {}
        for q in self._fresh(self._chain):
            if q.symbol in symbols:
                if self.requote_scale != 1.0:
                    q = OptionQuote(**{**q.__dict__, "bid": round(q.bid * self.requote_scale, 2),
                                       "ask": round(q.ask * self.requote_scale, 2)})
                out[q.symbol] = q
        return out

    def headlines(self, symbols, hours=18, limit=25):
        return [{"headline": "S&P 500 flat ahead of Broadcom earnings", "created_at": "x", "symbols": ["SPY"]}]

    def set_broker_positions_from_book(self, book):
        self._positions = []
        for p in book:
            if p.status == "closed":
                continue
            for l in p.legs:
                q = int(l["ratio"]) * p.contracts
                self._positions.append({"symbol": l["symbol"], "asset_class": "us_option", "qty": q,
                                        "side": "long" if l["side"] == "buy" else "short", "avg_entry_price": 1.0,
                                        "market_value": 0.0, "unrealized_pl": 0.0, "current_price": 1.0})


class FakeProvider:
    def __init__(self, model, payloads: dict[str, dict]):
        self.model = model
        self.payloads = payloads
        self.calls = 0

    def sampling_params(self):
        return {"temperature": 0.0, "top_p": 1e-6, "top_k": 1, "seed": 7, "model": self.model}

    def complete_json(self, system, user, schema, max_tokens=600):
        self.calls += 1
        key = schema.__name__
        parsed = schema.model_validate(self.payloads[key])
        return LLMResult(parsed=parsed, raw_text=json.dumps(self.payloads[key]), model=self.model, prompt_hash="p",
                         response_hash="r", latency_ms=5, tokens_in=100, tokens_out=20)


REGIME_OK = {"RegimeSchema": {"vol_regime": "low", "trend": "chop", "event_risk": "scheduled_minor",
                              "strategy_family": "IRON_CONDOR_0DTE", "veto": False, "veto_reason": "", "rationale": "calm"},
             "CriticSchema": {"verdict": "PASS", "reason": "consistent"},
             "JournalSchema": {"entry": "fake entry", "lesson": ""}}


def set_pilot(ag, first_live_order_contracts: int) -> None:
    """Settings are frozen mappings (immutable config, gate 27); swap in a frozen copy with the pilot flag changed."""
    from agent.core.config import _freeze
    d = dict(ag.s.strategy)
    d["sizing"] = {**ag.s.strategy["sizing"], "first_live_order_contracts": first_live_order_contracts}
    ag.s.strategy = _freeze(d)


def build_agent(state_dir, monkeypatch, payloads=None):
    """An agent wired to fakes, with its state in state_dir and an LLM that returns `payloads`."""
    payloads = payloads or REGIME_OK
    state_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = state_dir
    monkeypatch.setattr(main_mod, "STATE_DIR", tmp_path)
    monkeypatch.setattr(main_mod, "datetime", FakeClock)
    monkeypatch.setattr(main_mod.cboe, "fetch_term_structure",
                        lambda: {"vix": 16.3, "vix3m": 18.3, "vix1d": 10.8, "ts": FakeClock.now(timezone.utc), "source": "fake"})
    monkeypatch.setattr(main_mod.cboe, "vix1d_top_tercile_threshold", lambda n: 20.0)
    monkeypatch.setattr(main_mod.cboe, "closes_before", lambda sym, day, n=1: [16.0] * n)
    # a calibrated conformal state, so gate 31 has scores to read P from (see tests/test_conformal.py)
    from tests.test_conformal import synthetic_state
    synthetic_state().save(tmp_path / "conformal.json")
    import agent.execution.orders as orders_mod
    monkeypatch.setattr(orders_mod.time, "sleep", lambda s: None)
    monkeypatch.setattr(main_mod.time, "sleep", lambda s: None)
    ag = main_mod.Agent()
    set_pilot(ag, 1)   # the pilot rule is under test whatever the live config says
    chain = synthetic_chain(ts=FakeClock.now(timezone.utc))
    trading = FakeTrading()
    ag.data = FakeData(chain, trading)
    ag.walker.trading = trading
    mono = {"t": 1000.0}

    def fake_sleep(s):
        mono["t"] += s

    ag.walker.sleep = fake_sleep
    ag.walker.now = lambda: mono["t"]
    ag.strong = FakeProvider("fake-strong", payloads)
    ag.cheap = FakeProvider("fake-cheap", payloads)
    ag.journal.provider = ag.cheap
    return ag


@pytest.fixture
def agent(tmp_path, monkeypatch):
    return build_agent(tmp_path, monkeypatch, REGIME_OK)


def _kinds(ag):
    return [r["kind"] for r in ag.audit.read_all()]


def test_full_cycle_opens_then_take_profit_closes(agent):
    ag = agent
    ag.walker.trading.fill_at_rung = None      # first: nothing fills -> open_not_filled
    ag.cycle()
    kinds = _kinds(ag)
    assert "llm_regime" in kinds and "gates" in kinds and "llm_critic" in kinds and "execute_start" in kinds
    assert "open_not_filled" in kinds
    gates = [r for r in ag.audit.read_all() if r["kind"] == "gates"][-1]
    assert gates["passed"], [g for g in gates["results"] if not g["passed"]]
    assert ag.state.orders_sent == len([k for k in kinds if k == "order_submitted"]) >= 3
    assert gates["candidate"]["contracts"] == 1     # pilot lot on the first order of the campaign
    assert ag.walker.trading.last_signed_limit < 0  # Alpaca mleg: credit packages carry a NEGATIVE limit price

    # second cycle: duplicate-order gate must block the identical package inside 60 s
    ag.cycle()
    last = [r for r in ag.audit.read_all() if r["kind"] == "no_trade"][-1]
    assert "gate_duplicate_order" in last["reason"]

    # 2 minutes later, let the natural rung fill
    FakeClock.current += timedelta(seconds=130)
    exe = [r for r in ag.audit.read_all() if r["kind"] == "execute_start"][-1]
    ag.walker.trading.fill_at_rung = exe["prices"][-1]
    ag.cycle()
    opened = [r for r in ag.audit.read_all() if r["kind"] == "position_opened"]
    assert len(opened) == 1
    pos = opened[0]["position"]
    assert pos["contracts"] == 1 and pos["entry_credit"] == pytest.approx(exe["prices"][-1])
    assert opened[0]["fill_rung"] == len(exe["prices"]) - 1
    assert ag.state.risk_committed == pytest.approx(pos["max_loss_total"])
    assert (ag.book_store.path).exists()

    # broker now shows the legs; reconciliation must pass and no halt occur
    ag.data.set_broker_positions_from_book(ag.book)
    FakeClock.current += timedelta(seconds=30)
    ag.walker.trading.fill_at_rung = None
    ag.cycle()
    assert not ag.state.halted, ag.state.halt_reason

    # take profit: shrink every leg quote to 10 % so the package can be bought back cheaply
    cheap_chain = [OptionQuote(**{**q.__dict__, "bid": round(q.bid * 0.1, 2), "ask": round(q.ask * 0.1 + 0.01, 2),
                                  "quote_ts": FakeClock.now(timezone.utc)}) for q in ag.data._chain]
    ag.data._chain = cheap_chain
    FakeClock.current += timedelta(seconds=30)
    flat = [r for r in ag.audit.read_all() if r["kind"] == "flatten_start"]
    assert not flat
    # the closing walker fills at its first rung (closing mid)
    ag.walker.trading.fill_at_rung = None
    from agent.execution.flatten import closing_prices
    p = ag.open_positions()[0]
    mid, nat, ladder = closing_prices(p, ag.data.snapshots([l["symbol"] for l in p.legs]), 0.25, [0.0, 0.5, 1.0])
    assert mid < p.entry_credit * 0.5
    ag.walker.trading.fill_at_rung = ladder[0]
    ag.cycle()
    closed = [r for r in ag.audit.read_all() if r["kind"] == "position_closed"]
    assert len(closed) == 1 and closed[0]["pnl"] > 0 and "take profit" in closed[0]["reason"]
    assert ag.open_positions() == []
    assert ag.state.realized_pnl == pytest.approx(closed[0]["pnl"])


def test_recon_mismatch_halts(agent):
    ag = agent
    ag.data._positions = [{"symbol": "SPY260902C00700000", "asset_class": "us_option", "qty": 1, "side": "short",
                           "avg_entry_price": 1, "market_value": 0, "unrealized_pl": 0, "current_price": 1}]
    ag.cycle()
    assert ag.state.halted and "reconciliation" in ag.state.halt_reason
    assert "recon_position_mismatch" in _kinds(ag)


def test_llm_disagreement_forces_no_trade(agent, monkeypatch):
    ag = agent
    payload_a = REGIME_OK["RegimeSchema"]
    payload_b = {**payload_a, "strategy_family": "NO_TRADE", "veto": True, "veto_reason": "unsure"}
    seq = iter([payload_a, payload_b, payload_a])

    class Flip(FakeProvider):
        def complete_json(self, system, user, schema, max_tokens=600):
            if schema.__name__ == "RegimeSchema":
                self.payloads = {**self.payloads, "RegimeSchema": next(seq)}
            return super().complete_json(system, user, schema, max_tokens)

    ag.strong = Flip("fake-strong", REGIME_OK)
    ag.cycle()
    reg = [r for r in ag.audit.read_all() if r["kind"] == "llm_regime"][-1]
    assert reg["meta"]["unanimous"] is False
    assert reg["decision"]["strategy_family"] == "NO_TRADE" and reg["decision"]["veto"] is True
    assert "execute_start" not in _kinds(ag)


def test_kill_switch_file_halts(agent, tmp_path):
    ag = agent
    kill = main_mod.ROOT / ag.s.risk["kill_switch_file"]
    kill.parent.mkdir(exist_ok=True)
    try:
        kill.write_text("test")
        ag.cycle()
        assert ag.state.halted and "kill" in ag.state.halt_reason
        assert "kill_switch" in _kinds(ag)
    finally:
        kill.unlink(missing_ok=True)


def test_friday_is_no_trade(agent):
    ag = agent
    FakeClock.current = datetime(2026, 9, 4, 10, 5, tzinfo=ET).astimezone(timezone.utc)
    try:
        ag.cycle()
        kinds = _kinds(ag)
        assert "no_trade" in kinds and "execute_start" not in kinds and "llm_regime" not in kinds
    finally:
        FakeClock.current = datetime(2026, 9, 2, 10, 20, tzinfo=ET).astimezone(timezone.utc)


def test_candidate_is_byte_identical_across_llm_outputs(tmp_path, monkeypatch):
    """The LLM can only veto. Two agents whose models tell different stories (different enums, different prose,
    numbers in the rationale) and do not veto must produce the byte-identical order: strikes, wings, credit, contracts,
    ladder and collar. The numbers never pass through the model."""
    other = {**REGIME_OK,
             "RegimeSchema": {**REGIME_OK["RegimeSchema"], "vol_regime": "normal", "trend": "up", "event_risk": "none",
                              "rationale": "an entirely different narrative citing 3 catalysts, a 9.9 % move and a 0.55 delta"},
             "CriticSchema": {"verdict": "PASS", "reason": "different words, same verdict"}}
    execs, gates = [], []
    for name, payloads in (("a", REGIME_OK), ("b", other)):
        ag = build_agent(tmp_path / name, monkeypatch, payloads)
        ag.walker.trading.fill_at_rung = None
        ag.cycle()
        recs = ag.audit.read_all()
        execs.append([r for r in recs if r["kind"] == "execute_start"][-1])
        gates.append([r for r in recs if r["kind"] == "gates"][-1])
        # the stories really were different
        reg = [r for r in recs if r["kind"] == "llm_regime"][-1]
        assert reg["decision"]["rationale"] == payloads["RegimeSchema"]["rationale"]
    strip = lambda r: {k: v for k, v in r.items() if k not in ("ts",)}  # noqa: E731
    assert json.dumps(strip(execs[0])["candidate"], sort_keys=True) == json.dumps(strip(execs[1])["candidate"], sort_keys=True)
    assert execs[0]["prices"] == execs[1]["prices"] and execs[0]["collar"] == execs[1]["collar"]
    assert json.dumps(gates[0]["candidate"], sort_keys=True) == json.dumps(gates[1]["candidate"], sort_keys=True)
    assert [g["passed"] for g in gates[0]["results"]] == [g["passed"] for g in gates[1]["results"]]


def test_first_order_is_full_size_when_pilot_is_off(tmp_path, monkeypatch):
    """first_live_order_contracts: 0 (the live config from 2026-09-03) sizes the first order from the budget."""
    ag = build_agent(tmp_path / "full", monkeypatch, REGIME_OK)
    set_pilot(ag, 0)
    ag.walker.trading.fill_at_rung = None
    ag.cycle()
    gates = [r for r in ag.audit.read_all() if r["kind"] == "gates"][-1]
    assert gates["passed"], [g for g in gates["results"] if not g["passed"]]
    qty = gates["candidate"]["contracts"]
    assert 2 <= qty <= 5, qty   # more than the pilot lot, never above the per-order cap


def test_ladder_requotes_before_each_rung(tmp_path, monkeypatch):
    """Pilot 2026-09-02: rungs computed once at the decision were all above the natural by the time they were
    live. Now each rung is re-derived from fresh quotes; the fill price follows the market, not the stale plan."""
    ag = build_agent(tmp_path / "rq", monkeypatch, REGIME_OK)
    ag.data.requote_scale = 0.9            # credit decays 10 % between the decision chain and the ladder
    ag.walker.trading.fill_at_step = 1     # nothing fills at the mid rung, the second rung fills
    ag.cycle()
    recs = ag.audit.read_all()
    start = [r for r in recs if r["kind"] == "execute_start"][-1]
    subs = [r for r in recs if r["kind"] == "order_submitted"]
    opened = [r for r in recs if r["kind"] == "position_opened"]
    assert start["requote"] and start["rung_offsets"][:3] == [0, 1, 2] and start["rung_offsets"][-1] is None
    assert len(subs) == 2 and opened, [r["kind"] for r in recs][-8:]
    planned_mid = start["candidate"]["credit_mid"]
    fresh_mid = subs[1]["fresh_mid"]
    assert fresh_mid == pytest.approx(0.9 * planned_mid, abs=0.03)          # the re-quote saw the decayed market
    assert subs[1]["price"] == pytest.approx(round(fresh_mid - 0.01, 2), abs=1e-9)   # rung 1 = fresh mid - 1 tick
    assert subs[1]["price"] < subs[1]["planned_price"]                       # below the stale plan
    assert opened[0]["fill_rung"] == 1 and opened[0]["position"]["entry_credit"] == pytest.approx(subs[1]["price"])
    assert subs[1]["price"] >= start["floor_credit"] - 1e-9                  # never below the gated credit floor


def test_reconcile_positions_accepts_alpaca_enum_strings():
    """alpaca-py stringifies enums ("PositionSide.LONG"); the pilot's false halt on 2026-09-02 came from a
    case-sensitive check that made every bought wing look short."""
    from agent.execution.recon import reconcile_positions
    book = [SimpleNamespace(status="open", contracts=1, legs=[
        {"symbol": "SPY260902C00769000", "side": "sell", "ratio": 1},
        {"symbol": "SPY260902C00772000", "side": "buy", "ratio": 1},
        {"symbol": "SPY260902P00763000", "side": "sell", "ratio": 1},
        {"symbol": "SPY260902P00760000", "side": "buy", "ratio": 1}])]
    broker = [
        {"symbol": "SPY260902C00769000", "asset_class": "AssetClass.US_OPTION", "qty": -1.0, "side": "PositionSide.SHORT"},
        {"symbol": "SPY260902C00772000", "asset_class": "AssetClass.US_OPTION", "qty": 1.0, "side": "PositionSide.LONG"},
        {"symbol": "SPY260902P00763000", "asset_class": "AssetClass.US_OPTION", "qty": -1.0, "side": "PositionSide.SHORT"},
        {"symbol": "SPY260902P00760000", "asset_class": "AssetClass.US_OPTION", "qty": 1.0, "side": "PositionSide.LONG"}]
    ok, problems = reconcile_positions(book, broker)
    assert ok and problems == []
    ok, problems = reconcile_positions(book, broker[:3])       # a missing wing is still a mismatch
    assert not ok and "SPY260902P00760000" in problems[0]
