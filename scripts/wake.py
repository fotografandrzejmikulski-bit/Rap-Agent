"""Bounded durable consciousness tick for GitHub Actions."""
from __future__ import annotations

import os

from src.omega.psychic import PsychicDynamics
from src.omega.state_store import StateStore


def main() -> None:
    store = StateStore(os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite"))
    state = PsychicDynamics(store)
    state.tick(stochastic=True)
    print("[Ω∞] durable wake complete")
    print(state.snapshot())


if __name__ == "__main__":
    main()
