"""Typed data models shared by every module.

Enums are the ONLY vocabulary the LLM is allowed to speak (gate 18: gate_llm_output_schema).
Everything numeric lives in dataclasses that are produced by code, never by the model.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import Enum
from typing import Optional


# --------------------------------------------------------------------------- enums (LLM vocabulary)
class VolRegime(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    ELEVATED = "elevated"
    STRESSED = "stressed"


class Trend(str, Enum):
    UP = "up"
    CHOP = "chop"
    DOWN = "down"


class EventRisk(str, Enum):
    NONE = "none"
    SCHEDULED_MINOR = "scheduled_minor"
    SCHEDULED_MAJOR = "scheduled_major"
    UNSCHEDULED = "unscheduled"


class StrategyFamily(str, Enum):
    IRON_CONDOR_0DTE = "IRON_CONDOR_0DTE"
    PUT_CREDIT_SPREAD = "PUT_CREDIT_SPREAD"
    CALL_CREDIT_SPREAD = "CALL_CREDIT_SPREAD"
    LONG_GAMMA_SLEEVE = "LONG_GAMMA_SLEEVE"
    NO_TRADE = "NO_TRADE"


class CriticVerdict(str, Enum):
    PASS = "PASS"
    REDUCE = "REDUCE"
    BLOCK = "BLOCK"


class Right(str, Enum):
    CALL = "call"
    PUT = "put"


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


# --------------------------------------------------------------------------- market data
@dataclass(frozen=True)
class UnderlyingQuote:
    symbol: str
    bid: float
    ask: float
    ts: datetime

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0


@dataclass(frozen=True)
class OptionQuote:
    """One contract snapshot as delivered by Alpaca (Black-Scholes Greeks, IV, NBBO)."""
    symbol: str            # OCC symbol, e.g. SPY260902C00650000
    underlying: str
    expiry: date
    strike: float
    right: Right
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    quote_ts: datetime
    iv: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def spread_pct_of_mid(self) -> float:
        return self.spread / self.mid if self.mid > 0 else float("inf")

    @property
    def is_quotable(self) -> bool:
        return self.bid > 0 and self.ask > 0 and self.ask >= self.bid


@dataclass(frozen=True)
class RegimeSnapshot:
    """Volatility term structure from Cboe (delayed) plus realised intraday vol from bars."""
    ts: datetime
    vix: float
    vix3m: float
    vix1d: Optional[float]
    realized_vol_annualized: Optional[float]   # from 5-min SPY bars today, annualised
    source: str

    @property
    def slope(self) -> float:
        return self.vix / self.vix3m if self.vix3m > 0 else float("inf")


# --------------------------------------------------------------------------- strategy objects
@dataclass(frozen=True)
class Leg:
    quote: OptionQuote
    side: Side
    ratio: int = 1

    @property
    def signed_ratio(self) -> int:
        return self.ratio if self.side == Side.BUY else -self.ratio


@dataclass
class CondorCandidate:
    """A fully specified, code-generated iron condor. Numbers only from code."""
    underlying: str
    expiry: date
    spot: float
    implied_move: float           # $ expected remaining-day |move| from the ATM straddle
    legs: list[Leg]               # short call, long call, short put, long put
    contracts: int                # package quantity (qty in the mleg order)
    credit_mid: float             # per package, per share ($), at leg mids
    credit_natural: float         # per package, per share ($), at the marketable side
    wing_width: float
    max_loss_per_package: float   # $, worst case for qty 1 at credit_mid
    net_delta: float              # per package (shares equivalent / 100)
    net_gamma: float
    net_theta: float
    net_vega: float
    created_ts: datetime
    rationale: str = ""
    extras: dict = field(default_factory=dict)   # e.g. the conformal P-vs-Q ledger (gate 31)

    @property
    def max_loss_total(self) -> float:
        return self.max_loss_per_package * self.contracts

    @property
    def credit_total_mid(self) -> float:
        return self.credit_mid * 100.0 * self.contracts

    @property
    def short_call(self) -> Leg:
        return next(l for l in self.legs if l.side == Side.SELL and l.quote.right == Right.CALL)

    @property
    def long_call(self) -> Leg:
        return next(l for l in self.legs if l.side == Side.BUY and l.quote.right == Right.CALL)

    @property
    def short_put(self) -> Leg:
        return next(l for l in self.legs if l.side == Side.SELL and l.quote.right == Right.PUT)

    @property
    def long_put(self) -> Leg:
        return next(l for l in self.legs if l.side == Side.BUY and l.quote.right == Right.PUT)

    def summary(self) -> dict:
        return {
            "underlying": self.underlying,
            "expiry": self.expiry.isoformat(),
            "spot": round(self.spot, 2),
            "implied_move": round(self.implied_move, 3),
            "short_call": self.short_call.quote.strike,
            "long_call": self.long_call.quote.strike,
            "short_put": self.short_put.quote.strike,
            "long_put": self.long_put.quote.strike,
            "call_ratio": self.short_call.ratio,
            "put_ratio": self.short_put.ratio,
            "contracts": self.contracts,
            "credit_mid": round(self.credit_mid, 3),
            "credit_natural": round(self.credit_natural, 3),
            "max_loss_per_package": round(self.max_loss_per_package, 2),
            "max_loss_total": round(self.max_loss_total, 2),
            "net_delta": round(self.net_delta, 4),
            "net_gamma": round(self.net_gamma, 5),
            "net_theta": round(self.net_theta, 4),
            "net_vega": round(self.net_vega, 4),
            "conformal": ({k: (round(v, 4) if isinstance(v, float) else v)
                           for k, v in self.extras["conformal"].items()
                           if k in ("k_conformal", "k_effective", "q_mid", "p_mid", "gap", "margin", "passes")}
                          if "conformal" in self.extras else None),
        }


# --------------------------------------------------------------------------- decisions
@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    reason: str
    value: Optional[float] = None
    limit: Optional[float] = None


@dataclass(frozen=True)
class RegimeDecision:
    """Validated LLM output. Only enums and text; produced by agent.llm.regime."""
    vol_regime: VolRegime
    trend: Trend
    event_risk: EventRisk
    strategy_family: StrategyFamily
    veto: bool
    veto_reason: str
    rationale: str
    model: str
    prompt_hash: str
    response_hash: str
    latency_ms: int
    tokens_in: int
    tokens_out: int


@dataclass(frozen=True)
class CriticDecision:
    verdict: CriticVerdict
    reason: str
    model: str
    prompt_hash: str
    response_hash: str
    latency_ms: int


@dataclass
class BookPosition:
    """Internal position book entry, reconciled each cycle against the broker (gate 22)."""
    position_id: str
    underlying: str
    expiry: date
    legs: list[dict]              # [{symbol, strike, right, side, ratio}]
    contracts: int
    entry_credit: float           # per share, per package, actually filled
    max_loss_total: float
    opened_ts: datetime
    entry_order_id: str
    closed_ts: Optional[datetime] = None
    exit_debit: Optional[float] = None
    exit_order_id: Optional[str] = None
    status: str = "open"          # open | closing | closed

    def to_dict(self) -> dict:
        d = asdict(self)
        d["expiry"] = self.expiry.isoformat()
        d["opened_ts"] = self.opened_ts.isoformat()
        d["closed_ts"] = self.closed_ts.isoformat() if self.closed_ts else None
        return d


@dataclass
class SessionState:
    """Mutable counters for the rate/throttle gates and the daily loss kill."""
    session_date: date
    orders_sent: int = 0
    fills: int = 0
    order_timestamps: list[datetime] = field(default_factory=list)
    recent_order_keys: dict = field(default_factory=dict)   # dedupe key -> ts
    realized_pnl: float = 0.0
    risk_committed: float = 0.0        # sum of max loss of positions opened today
    halted: bool = False
    halt_reason: str = ""
    positions_opened: int = 0
