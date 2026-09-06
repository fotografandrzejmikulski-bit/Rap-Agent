from __future__ import annotations

import math
import time
from typing import Any

import numpy as np

from .state_store import StateStore


class PsychicDynamics:
    """Durable computational affect dynamics; not a claim of sentience."""

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
        dt = max(0.0, min(now - self.timestamp, 3600.0))
        if dt <= 0:
            return
        self._evolve(dt, stochastic=False)
        self.timestamp = now
        self.state_version += 1
        self.persist()

    def _evolve(self, dt: float, stochastic: bool) -> None:
        decay = 1.0 - math.exp(-0.035 * max(0.0, dt))
        noise_scale = min(0.025, 0.002 * math.sqrt(max(dt, 0.0)))
        noise = np.random.normal(0.0, noise_scale, self.tensor.shape) if stochastic else np.zeros_like(self.tensor)
        drift = (self.BASELINE - self.tensor) * decay
        self.tensor = np.clip(self.tensor + drift + noise, 0.0, 1.0)
        mean_emotion = float(np.mean(self.tensor))
        spread = float(np.std(self.tensor))
        self.arousal = float(np.clip(0.78 * self.arousal + 0.22 * mean_emotion, 0.0, 1.0))
        self.valence = float(np.clip(self.valence * 0.98 + (self.tensor[5] - self.tensor[1]) * 0.02, -1.0, 1.0))
        self.coherence = float(np.clip(0.94 * self.coherence + 0.06 * (1.0 - spread), 0.0, 1.0))
        self.novelty_pressure = float(np.clip(0.992 * self.novelty_pressure + 0.008 * (1.0 - self.repetition_pressure), 0.0, 1.0))
        self.repetition_pressure = float(np.clip(self.repetition_pressure * math.exp(-0.004 * max(dt, 0.0)), 0.0, 1.0))

    def tick(self, stochastic: bool = True, elapsed_seconds: float | None = None) -> None:
        now = time.time()
        dt = max(0.0, elapsed_seconds if elapsed_seconds is not None else now - self.timestamp)
        self._evolve(dt, stochastic=stochastic)
        self.timestamp = now
        self.state_version += 1
        self.persist()

    def apply_stimulus(self, text: str) -> dict[str, float]:
        lowered = text.casefold()
        lexicon = {
            "anger": ("wkurw", "złość", "gniew", "wściek", "zemst"),
            "fear": ("strach", "lęk", "boję", "panik", "przeraż"),
            "nostalgia": ("dom", "dzieci", "wspomn", "kiedyś", "matka", "ojciec", "stary blok"),
            "pride": ("duma", "sukces", "honor", "zwycię", "szacun"),
            "paranoia": ("system", "polic", "podsłuch", "szpieg", "kłam", "monitor"),
            "hope": ("jutro", "nadzie", "zmiana", "wyjście", "wolność", "przyszłość"),
            "guilt": ("wina", "żał", "przepras", "krzywd", "wyrzut"),
            "apathy": ("nic", "pusto", "oboję", "bez sens", "wszystko jedno"),
        }
        delta = np.zeros_like(self.tensor)
        for i, dimension in enumerate(self.DIMENSIONS):
            hits = sum(lowered.count(marker) for marker in lexicon[dimension])
            if hits:
                delta[i] = min(0.18, 0.035 * hits)
        self.tensor = np.clip(self.tensor + delta, 0.0, 1.0)
        self.arousal = float(np.clip(self.arousal + np.linalg.norm(delta) * 1.8, 0.0, 1.0))
        self.valence = float(np.clip(self.valence + (float(delta[5]) - float(delta[1])) * 0.4, -1.0, 1.0))
        self.novelty_pressure = float(np.clip(self.novelty_pressure + 0.08, 0.0, 1.0))
        self.state_version += 1
        self.timestamp = time.time()
        self.persist()
        return {name: float(delta[i]) for i, name in enumerate(self.DIMENSIONS) if delta[i] > 0}

    def set_wandering_thought(self, thought: str) -> None:
        self.wandering_thought = thought.strip()[:4000]
        self.state_version += 1
        self.timestamp = time.time()
        self.persist()

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
