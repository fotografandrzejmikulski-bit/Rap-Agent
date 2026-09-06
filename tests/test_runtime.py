from pathlib import Path

from src.omega.runtime import OmegaRuntime


def test_runtime_persists_state(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "omega.sqlite"
    canon = tmp_path / "canon.json"
    monkeypatch.setenv("OMEGA_DB_PATH", str(db))
    monkeypatch.setenv("OMEGA_CANON_PATH", str(canon))

    runtime = OmegaRuntime.build()
    before = runtime.psychic.snapshot()["state_version"]
    runtime.psychic.tick(stochastic=False)
    after = runtime.psychic.snapshot()["state_version"]
    assert after == before + 1

    restarted = OmegaRuntime.build()
    assert restarted.psychic.snapshot()["state_version"] >= after


def test_wake_is_bounded(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OMEGA_DB_PATH", str(tmp_path / "omega.sqlite"))
    monkeypatch.setenv("OMEGA_CANON_PATH", str(tmp_path / "canon.json"))
