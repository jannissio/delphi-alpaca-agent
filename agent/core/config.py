"""Configuration loader.

Gate 29 (config_immutability): the YAML files under config/ are read once, hashed, and
exposed as read-only mappings. No module in agent/ imports a writer for them, and the
LLM never sees a file path. The config hash is stamped on every audit record and order
(gate 24: deploy_version_pin).
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
STATE_DIR = ROOT / "state"
LOG_DIR = ROOT / "logs"


def _freeze(obj: Any) -> Any:
    if isinstance(obj, dict):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_freeze(v) for v in obj)
    return obj


def _load_yaml(name: str) -> tuple[Mapping, str]:
    path = CONFIG_DIR / name
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()[:12]
    return _freeze(yaml.safe_load(raw)), digest


def git_commit_hash() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "nogit"
    except Exception:
        return "nogit"


class Settings:
    """Everything the agent needs to know at start-up. Read-only after construction."""

    def __init__(self) -> None:
        load_dotenv(ROOT / ".env")
        self.risk, self.risk_hash = _load_yaml("risk_limits.yaml")
        self.strategy, self.strategy_hash = _load_yaml("strategy.yaml")
        self.calendar, self.calendar_hash = _load_yaml("calendar.yaml")
        self.config_hash = hashlib.sha256(
            (self.risk_hash + self.strategy_hash + self.calendar_hash).encode()
        ).hexdigest()[:12]
        self.git_hash = git_commit_hash()

        self.alpaca_key = os.getenv("ALPACA_API_KEY", "")
        self.alpaca_secret = os.getenv("ALPACA_SECRET_KEY", "")
        self.alpaca_paper = os.getenv("ALPACA_PAPER_TRADE", "true").lower() != "false"
        self.alpaca_account_id = os.getenv("ALPACA_ACCOUNT_ID", "")
        self.featherless_key = os.getenv("FEATHERLESS_API_KEY", "")
        self.model_strong = os.getenv("FEATHERLESS_MODEL_STRONG", "deepseek-ai/DeepSeek-V3.2")
        self.model_cheap = os.getenv("FEATHERLESS_MODEL_CHEAP", "Qwen/Qwen3-30B-A3B-Instruct-2507")
        self.dry_run = os.getenv("AGENT_DRY_RUN", "false").lower() == "true"

        STATE_DIR.mkdir(exist_ok=True)
        LOG_DIR.mkdir(exist_ok=True)

    # convenience accessors -------------------------------------------------
    @property
    def capital(self) -> float:
        return float(self.risk["capital_base_usd"])

    @property
    def session_budget(self) -> float:
        return self.capital * float(self.risk["session_budget_pct"])

    @property
    def campaign_budget(self) -> float:
        return self.capital * float(self.risk["campaign_budget_pct"])

    def entry_windows(self, day_iso: str) -> list[list[str]]:
        w = self.strategy["entry_windows_et"].get(day_iso)
        return [list(x) for x in w] if w else []

    def enabled_underlyings(self) -> list[str]:
        return [u for u, cfg in self.strategy["underlyings"].items() if cfg.get("enabled")]

    def underlying_cfg(self, symbol: str) -> Mapping:
        return self.strategy["underlyings"][symbol]

    def require_alpaca(self) -> None:
        if not self.alpaca_key or not self.alpaca_secret:
            raise RuntimeError("ALPACA_API_KEY / ALPACA_SECRET_KEY missing in .env")
        if not self.alpaca_paper:
            raise RuntimeError("Refusing to start: ALPACA_PAPER_TRADE must be true for this agent")

    def describe(self) -> dict:
        return {
            "git": self.git_hash,
            "config_hash": self.config_hash,
            "risk_hash": self.risk_hash,
            "strategy_hash": self.strategy_hash,
            "calendar_hash": self.calendar_hash,
            "paper": self.alpaca_paper,
            "model_strong": self.model_strong,
            "model_cheap": self.model_cheap,
            "dry_run": self.dry_run,
        }
