from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from .state_store import StateStore


class AssociativeRetriever:
    """Hybrid symbolic retrieval: emotion affinity + recency + access + graph proximity."""

    def __init__(self, store: StateStore) -> None:
        self.store = store

    def rank(self, query_emotion: np.ndarray, memories: Iterable[dict], limit: int = 8) -> list[dict]:
        q = np.asarray(query_emotion, dtype=float)
        candidates = []
        now = max((float(m.get("last_accessed", 0.0)) for m in memories), default=0.0)
        for memory in memories:
            emotion = np.asarray(memory.get("emotion", q), dtype=float)
            norm = float(np.linalg.norm(q) * np.linalg.norm(emotion))
            affinity = float(np.dot(q, emotion) / norm) if norm else 0.0
            recency = math.exp(-max(0.0, now - float(memory.get("last_accessed", now))) / 86400.0)
            access = min(1.0, math.log1p(int(memory.get("access_count", 0))) / 5.0)
            score = 0.55 * affinity + 0.25 * recency + 0.20 * access
            candidates.append((score, memory))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in candidates[:limit]]
