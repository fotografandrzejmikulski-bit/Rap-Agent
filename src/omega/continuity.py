from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class ContinuityStore:
    """Append-only event/checkpoint layer for durable creator continuity."""

    def __init__(self, db_path: str = "data/omega_synapses.sqlite") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS continuity_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_continuity_events_type ON continuity_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_continuity_events_time ON continuity_events(created_at);
                CREATE TABLE IF NOT EXISTS forge_runs (
                    request_id TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    result_json TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _hash(event_type: str, payload: dict[str, Any]) -> str:
        canonical = json.dumps({"type": event_type, "payload": payload}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def append(self, event_type: str, payload: dict[str, Any]) -> str:
        event_hash = self._hash(event_type, payload)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO continuity_events(event_type,event_hash,payload,created_at) VALUES(?,?,?,?)",
                (event_type, event_hash, json.dumps(payload, ensure_ascii=False), time.time()),
            )
        return event_hash

    def save_forge(self, request_id: str, prompt: str, result: dict[str, Any]) -> None:
        prompt_hash = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO forge_runs(request_id,created_at,prompt_hash,result_json) VALUES(?,?,?,?)",
                (request_id, time.time(), prompt_hash, json.dumps(result, ensure_ascii=False)),
            )

    def load_forge(self, request_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT result_json FROM forge_runs WHERE request_id=?", (request_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def recent(self, event_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = "SELECT event_type,payload,created_at FROM continuity_events"
        params: tuple[Any, ...] = ()
        if event_type:
            query += " WHERE event_type=?"
            params = (event_type,)
        query += " ORDER BY event_id DESC LIMIT ?"
        params += (limit,)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [{"event_type": r[0], "payload": json.loads(r[1]), "created_at": r[2]} for r in rows]
