from __future__ import annotations

import json
import math
import random
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

import numpy as np


class AssociativeMemory:
    """Canonical persistent memory with bounded spreading activation."""

    def __init__(self, db_path: str = "data/omega_synapses.sqlite") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS omega_memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    canon INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS omega_links (
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    weight REAL NOT NULL DEFAULT 1.0,
                    PRIMARY KEY(source,target),
                    FOREIGN KEY(source) REFERENCES omega_memories(id) ON DELETE CASCADE,
                    FOREIGN KEY(target) REFERENCES omega_memories(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_omega_memories_access ON omega_memories(last_accessed);
                """
            )

    def add(
        self,
        content: str,
        emotion: Iterable[float],
        *,
        kind: str = "episodic",
        confidence: float = 1.0,
        canon: bool = False,
        related: Iterable[str] = (),
    ) -> str:
        node_id = f"m_{time.time_ns()}_{random.randrange(100000):05d}"
        now = time.time()
        vector = json.dumps([float(x) for x in emotion])
        related_ids = [rid for rid in related if self.exists(rid)]
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO omega_memories(id,content,kind,emotion,confidence,created_at,last_accessed,access_count,canon) VALUES(?,?,?,?,?,?,?,?,?)",
                (node_id, content, kind, vector, max(0.0, min(1.0, confidence)), now, now, 1, int(canon)),
            )
            for target in related_ids:
                conn.execute(
                    "INSERT OR REPLACE INTO omega_links(source,target,weight) VALUES(?,?,?)",
                    (node_id, target, 1.0),
                )
                conn.execute(
                    "INSERT OR REPLACE INTO omega_links(source,target,weight) VALUES(?,?,?)",
                    (target, node_id, 0.65),
                )
        return node_id

    def exists(self, node_id: str) -> bool:
        with self._connect() as conn:
            return conn.execute("SELECT 1 FROM omega_memories WHERE id=?", (node_id,)).fetchone() is not None

    def strengthen(self, source: str, target: str, amount: float = 0.08) -> None:
        with self._connect() as conn:
            row = conn.execute("SELECT weight FROM omega_links WHERE source=? AND target=?", (source, target)).fetchone()
            if row is None:
                return
            weight = min(5.0, float(row[0]) + amount)
            conn.execute("UPDATE omega_links SET weight=? WHERE source=? AND target=?", (weight, source, target))

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id,content,kind,emotion,confidence,created_at,last_accessed,access_count,canon FROM omega_memories ORDER BY last_accessed DESC LIMIT ?",
                (max(1, min(limit, 1000)),),
            ).fetchall()
        return [
            {
                "id": r[0], "content": r[1], "kind": r[2], "emotion": json.loads(r[3]),
                "confidence": r[4], "created_at": r[5], "last_accessed": r[6],
                "access_count": r[7], "canon": bool(r[8]),
            }
            for r in rows
        ]

    def spread(self, query_emotion: Iterable[float], limit: int = 8) -> list[dict[str, Any]]:
        q = np.asarray(list(query_emotion), dtype=float)
        candidates = self.recent(1000)
        scored: list[tuple[float, dict[str, Any]]] = []
        now = time.time()
        for item in candidates:
            v = np.asarray(item["emotion"], dtype=float)
            denom = float(np.linalg.norm(q) * np.linalg.norm(v))
            affinity = float(np.dot(q, v) / denom) if denom else 0.0
            recency = math.exp(-max(0.0, now - float(item["last_accessed"])) / 172800.0)
            frequency = min(1.0, math.log1p(int(item["access_count"])) / 6.0)
            confidence = float(item["confidence"])
            score = 0.52 * affinity + 0.18 * recency + 0.15 * frequency + 0.15 * confidence
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [item for _, item in scored[: max(1, min(limit, 24))]]
        with self._connect() as conn:
            now = time.time()
            for item in selected:
                conn.execute(
                    "UPDATE omega_memories SET last_accessed=?, access_count=access_count+1 WHERE id=?",
                    (now, item["id"]),
                )
        return selected
