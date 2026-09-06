import pytest
from pydantic import ValidationError

from src.omega.models import QualityVector


def test_quality_vector_weighted_score() -> None:
    q = QualityVector(
        identity=100, originality=100, emotional_truth=100,
        language=100, flow=100, musicality=100,
        voice=100, immersion=100, replay_value=100,
    )
    assert q.weighted == 100


def test_quality_vector_rejects_invalid_range() -> None:
    with pytest.raises(ValidationError):
        QualityVector(
            identity=101, originality=90, emotional_truth=90,
            language=90, flow=90, musicality=90,
            voice=90, immersion=90, replay_value=90,
        )
