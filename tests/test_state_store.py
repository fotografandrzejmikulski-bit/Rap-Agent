from pathlib import Path

import numpy as np

from src.omega.state_store import StateStore


def test_state_store_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "state.sqlite"
    store = StateStore(str(db))
    baseline = np.array([0.2, 0.4, 0.3], dtype=float)
    initial = store.load(("a", "b", "c"), baseline)
    initial["tensor"] = np.array([0.8, 0.1, 0.7])
    initial["wandering_thought"] = "zimny korytarz"
    initial["state_version"] = 7
    store.save(initial)

    loaded = store.load(("a", "b", "c"), baseline)
    assert np.allclose(loaded["tensor"], [0.8, 0.1, 0.7])
    assert loaded["wandering_thought"] == "zimny korytarz"
    assert loaded["state_version"] == 7
