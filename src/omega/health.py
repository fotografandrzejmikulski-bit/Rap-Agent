from __future__ import annotations

from typing import Any

from .canon import CreatorCanon
from .continuity import ContinuityStore
from .psychic import PsychicDynamics


class RuntimeHealth:
    def __init__(self, psychic: PsychicDynamics, continuity: ContinuityStore, canon: CreatorCanon) -> None:
        self.psychic = psychic
        self.continuity = continuity
        self.canon = canon

    def snapshot(self) -> dict[str, Any]:
        state = self.psychic.snapshot()
        events = self.continuity.recent(limit=3)
        return {
            "status": "READY",
            "state_version": state["state_version"],
            "state_timestamp": state["timestamp"],
            "canon_version": self.canon.data.get("version", 0),
            "recent_events": len(events),
            "integrity": {
                "state_in_range": all(0.0 <= v <= 1.0 for v in state["tensor"].values()),
                "arousal_in_range": 0.0 <= state["arousal"] <= 1.0,
                "coherence_in_range": 0.0 <= state["coherence"] <= 1.0,
            },
        }
