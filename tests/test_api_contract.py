from pathlib import Path

from src.omega.models import Critique, QualityVector
from src.omega.engine import ForgePolicy


def test_policy_rejects_low_originality_even_with_high_average() -> None:
    q = QualityVector(
        identity=99,
        originality=89,
        emotional_truth=99,
        language=99,
        flow=99,
        musicality=99,
        voice=99,
        immersion=99,
        replay_value=99,
    )
    passed, failures = ForgePolicy.validate(q)
    assert not passed
    assert "originality" in failures


def test_required_repository_artifacts_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for path in (
        "api.py",
        "README.md",
        "src/omega/psychic.py",
        "src/omega/state_store.py",
        "src/omega/memory.py",
        "src/omega/orchestrator.py",
        "config/system.json",
        ".github/workflows/ci.yml",
    ):
        assert (root / path).exists(), path
