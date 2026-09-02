"""Ticker and company-name anonymisation for LLM prompts.

Glasserman & Lin (2023) show LLM trading behaviour changes when tickers are visible
(memorised priors, look-ahead). We replace names with stable placeholders before any
text reaches the model, and keep the mapping only on the code side. The mapping is also
the basis of the leakage self-audit: the same prompt with and without masking must yield
the same enums.
"""
from __future__ import annotations

import re

# Longest patterns first so "S&P 500" is replaced before "S&P".
_PATTERNS: list[tuple[str, str]] = [
    (r"\bSPDR S&P 500( ETF)?( Trust)?\b", "INDEX_ETF_A"),
    (r"\bS&P ?500\b", "INDEX_A"),
    (r"\bS&P\b", "INDEX_A"),
    (r"\bSPX\b", "INDEX_A"),
    (r"\bSPY\b", "INDEX_ETF_A"),
    (r"\bInvesco QQQ( Trust)?\b", "INDEX_ETF_B"),
    (r"\bNasdaq[- ]?100\b", "INDEX_B"),
    (r"\bNasdaq\b", "INDEX_B"),
    (r"\bQQQ\b", "INDEX_ETF_B"),
    (r"\bDow Jones( Industrial Average)?\b", "INDEX_C"),
    (r"\bBroadcom\b", "COMPANY_1"),
    (r"\bAVGO\b", "COMPANY_1"),
    (r"\bSnowflake\b", "COMPANY_2"),
    (r"\bSNOW\b", "COMPANY_2"),
    (r"\bHewlett Packard Enterprise\b", "COMPANY_3"),
    (r"\bHPE\b", "COMPANY_3"),
    (r"\bZscaler\b", "COMPANY_4"),
    (r"\bZS\b", "COMPANY_4"),
    (r"\bLululemon\b", "COMPANY_5"),
    (r"\bLULU\b", "COMPANY_5"),
    (r"\bDocuSign\b", "COMPANY_6"),
    (r"\bDOCU\b", "COMPANY_6"),
    (r"\bSamsara\b", "COMPANY_7"),
    (r"\bIOT\b", "COMPANY_7"),
    (r"\bCiena\b", "COMPANY_8"),
    (r"\bCIEN\b", "COMPANY_8"),
    (r"\bNvidia\b", "COMPANY_9"),
    (r"\bNVDA\b", "COMPANY_9"),
    (r"\bApple\b", "COMPANY_10"),
    (r"\bAAPL\b", "COMPANY_10"),
    (r"\bMicrosoft\b", "COMPANY_11"),
    (r"\bMSFT\b", "COMPANY_11"),
    (r"\bTesla\b", "COMPANY_12"),
    (r"\bTSLA\b", "COMPANY_12"),
    (r"\bFederal Reserve\b", "CENTRAL_BANK"),
    (r"\bFed\b", "CENTRAL_BANK"),
]
_COMPILED = [(re.compile(p, re.I), r) for p, r in _PATTERNS]
_TICKER = re.compile(r"\$[A-Z]{1,5}\b")


def anonymize(text: str) -> str:
    out = text
    for rx, rep in _COMPILED:
        out = rx.sub(rep, out)
    out = _TICKER.sub("$TICKER", out)
    return out


_HTML_TAG = re.compile(r"<[^>]{0,200}>")
_HIDDEN = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u00ad\u202a-\u202e\u2066-\u2069\u180e]")   # zero-width, soft hyphen, bidi controls
HEADLINE_MAX_CHARS = 240


def sanitize_text(text: str, max_chars: int = HEADLINE_MAX_CHARS) -> str:
    """Defence against adversarial news (Rizvani, Apruzzese & Laskov, SaTML 2026: Unicode homoglyphs and hidden text
    cut a news-driven strategy's annual return by up to 17.7 points): NFKC-normalise so homoglyphs collapse to their
    ASCII forms, drop zero-width and bidi control characters, strip HTML, collapse whitespace, cap the length."""
    import unicodedata
    t = unicodedata.normalize("NFKC", str(text))
    t = _HIDDEN.sub("", t)
    t = _HTML_TAG.sub(" ", t)
    t = "".join(ch for ch in t if ch == " " or (unicodedata.category(ch)[0] != "C"))   # other control characters
    t = " ".join(t.split())
    return t[:max_chars]


def anonymize_headlines(items: list[dict], now=None) -> list[str]:
    """Masked headline text prefixed with its age in hours (the model needs recency, not dates); every headline is
    sanitised first (see sanitize_text) and the provenance tag is the age, never the source URL."""
    from datetime import datetime, timezone
    now = now or datetime.now(tz=timezone.utc)
    out = []
    for i in items:
        h = sanitize_text(i.get("headline") or "")
        if not h:
            continue
        age = ""
        try:
            ts = datetime.fromisoformat(str(i.get("created_at", "")).replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            hours = (now - ts).total_seconds() / 3600.0
            age = f"[{hours:.0f}h ago] " if hours >= 1 else "[<1h ago] "
        except (ValueError, TypeError):
            pass
        out.append(age + anonymize(h))
    return out
