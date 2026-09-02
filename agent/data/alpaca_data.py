"""Alpaca market data and account access through alpaca-py.

Market data: option chain snapshots with Greeks/IV (indicative feed on the basic plan),
underlying NBBO, intraday bars for realised vol, Benzinga news headlines.
Trading: account, positions, orders, clock. Order *submission* lives in agent.execution.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from alpaca.data.enums import DataFeed, OptionsFeed
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import (NewsRequest, OptionChainRequest, OptionSnapshotRequest,
                                  StockBarsRequest, StockLatestQuoteRequest, StockLatestTradeRequest)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

from agent.core.models import OptionQuote, Right, UnderlyingQuote

log = logging.getLogger(__name__)


def parse_occ(symbol: str) -> tuple[str, date, Right, float]:
    """SPY260902C00650000 -> ('SPY', 2026-09-02, CALL, 650.0)."""
    root = symbol[:-15]
    yymmdd = symbol[-15:-9]
    right = Right.CALL if symbol[-9] == "C" else Right.PUT
    strike = int(symbol[-8:]) / 1000.0
    exp = date(2000 + int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6]))
    return root, exp, right, strike


class AlpacaData:
    def __init__(self, key: str, secret: str, paper: bool = True, feed: str = "indicative"):
        self.trading = TradingClient(key, secret, paper=paper)
        self.options = OptionHistoricalDataClient(key, secret)
        self.stocks = StockHistoricalDataClient(key, secret)
        self.news = NewsClient(key, secret)
        self.feed = OptionsFeed.OPRA if feed == "opra" else OptionsFeed.INDICATIVE

    # ------------------------------------------------------------------ account
    def account(self) -> dict:
        a = self.trading.get_account()
        return {
            "id": str(a.id), "account_number": a.account_number, "status": str(a.status),
            "equity": float(a.equity), "cash": float(a.cash), "buying_power": float(a.buying_power),
            "options_buying_power": float(getattr(a, "options_buying_power", 0) or 0),
            "options_approved_level": getattr(a, "options_approved_level", None),
            "options_trading_level": getattr(a, "options_trading_level", None),
            "last_equity": float(a.last_equity),
        }

    def clock(self) -> dict:
        c = self.trading.get_clock()
        return {"is_open": c.is_open, "next_open": c.next_open, "next_close": c.next_close, "timestamp": c.timestamp}

    def positions(self) -> list[dict]:
        out = []
        for p in self.trading.get_all_positions():
            out.append({
                "symbol": p.symbol, "asset_class": str(p.asset_class), "qty": float(p.qty),
                "side": str(p.side), "avg_entry_price": float(p.avg_entry_price),
                "market_value": float(p.market_value or 0), "unrealized_pl": float(p.unrealized_pl or 0),
                "current_price": float(p.current_price or 0),
            })
        return out

    def open_orders(self) -> list:
        return self.trading.get_orders(GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=200, nested=True))

    def orders_today(self) -> list:
        after = datetime.now(tz=timezone.utc) - timedelta(hours=20)
        return self.trading.get_orders(GetOrdersRequest(status=QueryOrderStatus.ALL, after=after, limit=500, nested=True))

    # ------------------------------------------------------------------ market data
    def underlying_quote(self, symbol: str) -> UnderlyingQuote:
        """IEX NBBO (the basic plan cannot query recent SIP data); falls back to the last trade
        when one side is missing (pre-market / stale)."""
        q = self.stocks.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=symbol, feed=DataFeed.IEX))[symbol]
        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
        if bid <= 0 or ask <= 0 or ask < bid:
            t = self.stocks.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol, feed=DataFeed.IEX))[symbol]
            px = float(t.price)
            return UnderlyingQuote(symbol=symbol, bid=px, ask=px, ts=t.timestamp)
        return UnderlyingQuote(symbol=symbol, bid=bid, ask=ask, ts=q.timestamp)

    def intraday_closes(self, symbol: str, minutes: int = 5) -> list[float]:
        now = datetime.now(tz=timezone.utc)
        start = now.replace(hour=13, minute=30, second=0, microsecond=0)   # 09:30 ET (EDT)
        if now <= start + timedelta(minutes=minutes):
            return []
        req = StockBarsRequest(symbol_or_symbols=symbol, timeframe=TimeFrame(minutes, TimeFrameUnit.Minute),
                               start=start, limit=200, feed=DataFeed.IEX)
        bars = self.stocks.get_stock_bars(req)
        data = bars.data.get(symbol, []) if hasattr(bars, "data") else bars[symbol]
        return [float(b.close) for b in data]

    def chain(self, underlying: str, expiry: date, spot: float, width_pct: float = 0.03) -> list[OptionQuote]:
        """Both sides of the chain for one expiry within +-width_pct of spot, with Greeks."""
        req = OptionChainRequest(
            underlying_symbol=underlying, feed=self.feed, expiration_date=expiry,
            strike_price_gte=round(spot * (1 - width_pct), 2), strike_price_lte=round(spot * (1 + width_pct), 2),
        )
        snaps = self.options.get_option_chain(req)
        return [self._to_quote(sym, s) for sym, s in snaps.items() if s is not None]

    def snapshots(self, symbols: list[str]) -> dict[str, OptionQuote]:
        out: dict[str, OptionQuote] = {}
        for i in range(0, len(symbols), 100):
            chunk = symbols[i:i + 100]
            snaps = self.options.get_option_snapshot(OptionSnapshotRequest(symbol_or_symbols=chunk, feed=self.feed))
            for sym, s in snaps.items():
                if s is not None:
                    out[sym] = self._to_quote(sym, s)
        return out

    @staticmethod
    def _to_quote(symbol: str, s) -> OptionQuote:
        root, exp, right, strike = parse_occ(symbol)
        lq = s.latest_quote
        g = s.greeks
        return OptionQuote(
            symbol=symbol, underlying=root, expiry=exp, strike=strike, right=right,
            bid=float(lq.bid_price) if lq else 0.0, ask=float(lq.ask_price) if lq else 0.0,
            bid_size=int(lq.bid_size) if lq else 0, ask_size=int(lq.ask_size) if lq else 0,
            quote_ts=lq.timestamp if lq else datetime(1970, 1, 1, tzinfo=timezone.utc),
            iv=float(s.implied_volatility) if s.implied_volatility is not None else None,
            delta=float(g.delta) if g and g.delta is not None else None,
            gamma=float(g.gamma) if g and g.gamma is not None else None,
            theta=float(g.theta) if g and g.theta is not None else None,
            vega=float(g.vega) if g and g.vega is not None else None,
        )

    def headlines(self, symbols: list[str], hours: int = 18, limit: int = 25) -> list[dict]:
        """Benzinga headlines via Alpaca News API; the LLM sees them anonymised."""
        try:
            start = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
            req = NewsRequest(symbols=",".join(symbols), start=start, limit=limit, sort="desc")
            res = self.news.get_news(req)
            items = res.data.get("news", []) if hasattr(res, "data") else res.news
            return [{"headline": n.headline, "created_at": n.created_at.isoformat(), "symbols": list(n.symbols or [])}
                    for n in items]
        except Exception as exc:
            log.warning("news fetch failed: %s", exc)
            return []
