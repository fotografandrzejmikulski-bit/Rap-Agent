from pathlib import Path

import numpy as np

from src.omega.psychic import PsychicDynamics
from src.omega.state_store import StateStore


def test_psychic_state_survives_restart(tmp_path: Path) -> None:
    db = tmp_path / "omega.sqlite"
    store = StateStore(str(db))
    first = PsychicDynamics(store)
    first.apply_stimulus("złość i strach, ale jutro jest wolność")
    snapshot = first.snapshot()

    second = PsychicDynamics(store)
    restored = second.snapshot()
    assert restored["state_version"] >= snapshot["state_version"]
    assert np.linalg.norm(
        np.array(list(restored["tensor"].values())) - np.array(list(snapshot["tensor"].values()))
    ) < 0.05


def test_psychic_decay_moves_toward_baseline(tmp_path: Path) -> None:
    db = tmp_path / "omega.sqlite"
    store = StateStore(str(db))
    state = PsychicDynamics(store)
    state.tensor = np.ones(8)
    state.timestamp -= 100
    state.tick(stochastic=False)
    assert np.all(state.tensor <= 1.0)
    assert np.mean(state.tensor) < 1.0
