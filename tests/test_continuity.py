import json
from pathlib import Path

from src.omega.continuity import ContinuityStore
from src.omega.engine import ArtifactHasher, ForgePolicy
from src.omega.models import QualityVector, Critique


def test_event_deduplication(tmp_path: Path) -> None:
    store = ContinuityStore(str(tmp_path / "omega.sqlite"))
    payload = {"x": 1, "nested": [2, 3]}
    first = store.append("tick", payload)
    second = store.append("tick", payload)
    assert first == second
    assert len(store.recent("tick")) == 1


def test_artifact_hash_is_stable() -> None:
    assert ArtifactHasher.text(["A", "B"]) == ArtifactHasher.text(["A", "B"])
    assert ArtifactHasher.text(["A", "B"]) != ArtifactHasher.text(["A", "C"])


def test_quality_policy_has_veto_dimensions() -> None:
    q = QualityVector(
        identity=89, originality=100, emotional_truth=100, language=100, flow=100,
        musicality=100, voice=100, immersion=100, replay_value=100,
    )
    passed, failures = ForgePolicy.validate(q)
    assert not passed
    assert "identity" in failures


def test_critique_model_accepts_line_rejections() -> None:
    c = Critique(global_score=92, rejected_lines=[])
    assert c.global_score == 92
