from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

from .canon import CreatorCanon
from .continuity import ContinuityStore
from .psychic import PsychicDynamics
from .state_store import StateStore


@dataclass
class OmegaRuntime:
    """Single canonical runtime composition root."""

    state_store: StateStore
    continuity: ContinuityStore
    psychic: PsychicDynamics
    canon: CreatorCanon

    @classmethod
    def build(cls) -> "OmegaRuntime":
        db = os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite")
        state_store = StateStore(db)
        continuity = ContinuityStore(db)
        return cls(
            state_store=state_store,
            continuity=continuity,
            psychic=PsychicDynamics(state_store),
            canon=CreatorCanon(os.environ.get("OMEGA_CANON_PATH", "config/canon.json")),
        )

    async def wake(self, ticks: int = 1) -> None:
        for _ in range(max(1, ticks)):
            self.psychic.tick(stochastic=True)
            self.continuity.append("psychic.tick", self.psychic.snapshot())
            await asyncio.sleep(0)
