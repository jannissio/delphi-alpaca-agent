"""Append-only audit log (gate 27) and position book persistence.

One JSON object per line in state/audit.jsonl. Every record carries the git commit and the
config hash (gate 24: deploy_version_pin). The post-session report and the determinism
replay are computed from this file alone.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone, date
from enum import Enum
from pathlib import Path
from typing import Any


def _default(o: Any):
    if isinstance(o, (datetime,)):
        return o.isoformat()
    if isinstance(o, date):
        return o.isoformat()
    if isinstance(o, Enum):
        return o.value
    if hasattr(o, "to_dict"):
        return o.to_dict()
    if hasattr(o, "__dict__"):
        return {k: v for k, v in o.__dict__.items() if not k.startswith("_")}
    return str(o)


class AuditLog:
    def __init__(self, path: Path, git_hash: str, config_hash: str, session_tag: str):
        self.path = path
        self.git = git_hash
        self.cfg = config_hash
        self.session = session_tag
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, kind: str, **fields: Any) -> dict:
        rec = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "kind": kind,
            "session": self.session,
            "git": self.git,
            "config": self.cfg,
            **fields,
        }
        line = json.dumps(rec, default=_default, ensure_ascii=False)
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())
        return rec

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]


class JsonState:
    """Tiny JSON persistence for the position book and session counters."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, default: Any) -> Any:
        if not self.path.exists():
            return default
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default

    def save(self, obj: Any) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, default=_default, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)
