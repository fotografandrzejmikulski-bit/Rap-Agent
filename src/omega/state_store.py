from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

import numpy as np


class StateStore:
    """Durable store for the evolving psychic state and compact cognition snapshot."""

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS psychic_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    timestamp REAL NOT NULL,
                    tensor TEXT NOT NULL,
                    wandering_thought TEXT NOT NULL,
                    arousal REAL NOT NULL,
                    valence REAL NOT NULL,
                    coherence REAL NOT NULL,
                    inhibition REAL NOT NULL,
                    curiosity REAL NOT NULL,
                    social_distance REAL NOT NULL,
                    aggression REAL NOT NULL,
                    openness REAL NOT NULL,
                    novelty_pressure REAL NOT NULL,
                    repetition_pressure REAL NOT NULL,
                    state_version INTEGER NOT NULL
                )
            """)

    def load(self, dimensions: tuple[str, ...], baseline: np.ndarray) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT timestamp, tensor, wandering_thought, arousal, valence, coherence, inhibition, curiosity, social_distance, aggression, openness, novelty_pressure, repetition_pressure, state_version FROM psychic_state WHERE id=1").fetchone()
        if row is None:
            return {
                "timestamp": time.time(),
                "tensor": np.asarray(baseline, dtype=float),
                "wandering_thought": "Pustka po ostatniej myśli.",
                "arousal": 0.0,
                "valence": 0.0,
                "coherence": 1.0,
                "inhibition": 0.5,
                "curiosity": 0.5,
                "social_distance": 0.5,
                "aggression": 0.2,
                "openness": 0.5,
                "novelty_pressure": 0.5,
                "repetition_pressure": 0.0,
                "state_version": 0,
            }
        tensor = np.asarray(json.loads(row[1]), dtype=float)
        if tensor.shape != baseline.shape:
            tensor = np.asarray(baseline, dtype=float)
        return {
            "timestamp": float(row[0]),
            "tensor": tensor,
            "wandering_thought": str(row[2]),
            "arousal": float(row[3]),
            "valence": float(row[4]),
            "coherence": float(row[5]),
            "inhibition": float(row[6]),
            "curiosity": float(row[7]),
            "social_distance": float(row[8]),
            "aggression": float(row[9]),
            "openness": float(row[10]),
            "novelty_pressure": float(row[11]),
            "repetition_pressure": float(row[12]),
            "state_version": int(row[13]),
        }

    def save(self, state: dict[str, Any]) -> None:
        now = float(state.get("timestamp", time.time()))
        payload = (
            now,
            json.dumps(np.asarray(state["tensor"], dtype=float).tolist()),
            str(state.get("wandering_thought", "")),
            float(state.get("arousal", 0.0)),
            float(state.get("valence", 0.0)),
            float(state.get("coherence", 1.0)),
            float(state.get("inhibition", 0.5)),
            float(state.get("curiosity", 0.5)),
            float(state.get("social_distance", 0.5)),
            float(state.get("aggression", 0.2)),
            float(state.get("openness", 0.5)),
            float(state.get("novelty_pressure", 0.5)),
            float(state.get("repetition_pressure", 0.0)),
            int(state.get("state_version", 0)),
        )
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO psychic_state VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    timestamp=excluded.timestamp,
                    tensor=excluded.tensor,
                    wandering_thought=excluded.wandering_thought,
                    arousal=excluded.arousal,
                    valence=excluded.valence,
                    coherence=excluded.coherence,
                    inhibition=excluded.inhibition,
                    curiosity=excluded.curiosity,
                    social_distance=excluded.social_distance,
                    aggression=excluded.aggression,
                    openness=excluded.openness,
                    novelty_pressure=excluded.novelty_pressure,
                    repetition_pressure=excluded.repetition_pressure,
                    state_version=excluded.state_version
            """, payload)
