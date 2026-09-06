from __future__ import annotations

import math
import time
from typing import Any

import numpy as np

from .state_store import StateStore


class PsychicDynamics:
    """Persistent computational mood dynamics; explicitly not a claim of sentience."""

    DIMENSIONS = (
        "anger", "fear", "nostalgia", "pride", "paranoia", "hope", "guilt", "apathy",
    )

    BASELINE = np.array([0.20, 0.40, 0.30, 0.50, 0.60, 0.10, 0.50, 0.40], dtype=float)

    def __init__(self, store: StateStore) -> None:
        self.store = store
        loaded = store.load(self.DIMENSIONS, self.BASELINE)
        self.timestamp = float(loaded["timestamp"])
        self.tensor = np.asarray(loaded["tensor"], dtype=float)
        self.wandering_thought = str(loaded["wandering_thought"])
        self.arousal = float(loaded["arousal"])
        self.valence = float(loaded["valence"])
        self.coherence = float(loaded["coherence"])
        self.inhibition = float(loaded["inhibition"])
        self.curiosity = float(loaded["curiosity"])
        self.social_distance = float(loaded["social_distance"])
        self.aggression = float(loaded["aggression"])
        self.openness = float(loaded["openness"])
        self.novelty_pressure = float(loaded["novelty_pressure"])
        self.repetition_pressure = float(loaded["repetition_pressure"])
        self.state_version = int(loaded["state_version"])
        self.resume_from_elapsed_time()

    def resume_from_elapsed_time(self) -> None:
        now = time.time()
        dt = max(0.0, now - self.timestamp)
        if dt > 0:
            self._evolve(dt, stochastic=False)
            self.timestamp = now
            self.state_version += 1
            self.persist()

    def _evolve(self, dt: float, stochastic: bool) -> None:
        decay = 1.0 - math.exp(-0.035 * min(dt, 3600.0))
        noise = np.random.normal(0.0, min(0.025, 0.002 * math.sqrt(max(dt, 0.0))), self.tensor.shape) if stochastic else 0.0
        self.tensor = np.clip(self.tensor + (self.BASELINE - self.tensor) * decay + noise, 0.0, 1.0)
        mean_emotion = float(np.mean(self.tensor))
        spread = float(np.std(self.tensor))
        self.arousal = float(np.clip(0.75 * self.arousal + 0.25 * mean_emotion, 0, 1))
        self.coherence = float(np.clip(0.94 * self.coherence + 0.06 * (1.0 - spread), 0, 1))
        self.novelty_pressure = float(np.clip(0.995 * self.novelty_pressure + 0.002 * self.repetition_pressure, 0, 1))
        self.repetition_pressure = float(np.clip(0.997 * self.repetition_pressure, 0, 1))

    def tick(self, stochastic: bool = True) -> None:
        now = time.time()
        dt = max(0.0, now - self.timestamp)
        self._evolve(dt, stochastic=stochastic)
        self.timestamp = now
        self.state_version += 1
        self.persist()

    def apply_stimulus(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        lexicon = {
            "anger": ("wkurw", "złość", "gniew", "wściek", "zemst"),
            "fear": ("strach", "lęk", "boję", "panik"),
            "nostalgia": ("dom", "dzieci", "wspomn", "kiedyś", "matka", "ojciec"),
            "pride": ("duma", "sukces", "honor", "zwycię"),
            "paranoia": ("system", "polic", "podsłuch", "szpieg", "kłam"),
            "hope": ("jutro", "nadzie", "zmiana", "wyjście", "wolność"),
            "guilt": ("wina", "żał", "przepras", "krzywd"),
            "apathy": ("nic", "pusto", "oboję", "bez sens"),
        }
        delta = np.zeros_like(self.tensor)
        for i, dimension in enumerate(self.DIMENSIONS):
            delta[i] = sum(0.035 for marker in lexicon[dimension] if marker in lowered)
        self.tensor = np.clip(self.tensor + delta, 0, 1)
        self.arousal = float(np.clip(self.arousal + np.linalg.norm(delta) * 1.8, 0, 1))
        self.novelty_pressure = float(np.clip(self.novelty_pressure + 0.08, 0, 1))
        self.state_version += 1
        self.timestamp = time.time()
        self.persist()
        return {name: float(delta[i]) for i, name in enumerate(self.DIMENSIONS) if delta[i]}

    def persist(self) -> None:
        self.store.save({
            "timestamp": self.timestamp,
            "tensor": self.tensor,
            "wandering_thought": self.wandering_thought,
            "arousal": self.arousal,
            "valence": self.valence,
            "coherence": self.coherence,
            "inhibition": self.inhibition,
            "curiosity": self.curiosity,
            "social_distance": self.social_distance,
            "aggression": self.aggression,
            "openness": self.openness,
            "novelty_pressure": self.novelty_pressure,
            "repetition_pressure": self.repetition_pressure,
            "state_version": self.state_version,
        })

    def snapshot(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "tensor": {name: float(self.tensor[i]) for i, name in enumerate(self.DIMENSIONS)},
            "wandering_thought": self.wandering_thought,
            "arousal": self.arousal,
            "valence": self.valence,
            "coherence": self.coherence,
            "inhibition": self.inhibition,
            "curiosity": self.curiosity,
            "social_distance": self.social_distance,
            "aggression": self.aggression,
            "openness": self.openness,
            "novelty_pressure": self.novelty_pressure,
            "repetition_pressure": self.repetition_pressure,
            "state_version": self.state_version,
        }
