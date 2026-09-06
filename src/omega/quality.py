from __future__ import annotations

from .models import Critique, QualityVector
from .engine import ForgePolicy


class QualityJudge:
    """Deterministic policy layer. The LLM supplies evidence; policy makes the gate decision."""

    @staticmethod
    def vector(critique: Critique, line_count: int) -> QualityVector:
        g = float(critique.global_score)
        return QualityVector(
            identity=float(critique.identity_score),
            originality=float(critique.originality_score),
            emotional_truth=float(critique.emotional_truth_score),
            language=min(100.0, g + (1.0 if line_count >= 8 else -2.0)),
            flow=min(100.0, g),
            musicality=min(100.0, g),
            voice=min(100.0, (critique.identity_score + critique.immersion_score) / 2),
            immersion=float(critique.immersion_score),
            replay_value=min(100.0, (critique.originality_score + critique.immersion_score) / 2),
        )

    @staticmethod
    def gate(quality: QualityVector, critique: Critique) -> dict[str, object]:
        passed, failures = ForgePolicy.validate(quality)
        if critique.rejected_lines:
            passed = False
            failures = sorted(set([*failures, "unresolved_line_rejections"]))
        return {
            "passed": passed,
            "failures": failures,
            "weighted_score": round(quality.weighted, 3),
            "quality": quality.model_dump(),
        }
