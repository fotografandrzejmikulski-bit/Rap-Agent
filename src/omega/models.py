from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Rejection(BaseModel):
    line_id: str
    severity: Literal["critical", "major", "minor"]
    reason_codes: list[str] = Field(default_factory=list)
    reason: str
    replacement_strategy: Literal["REWRITE", "RECONTEXTUALIZE", "DELETE", "MERGE"]
    preserve: list[str] = Field(default_factory=list)


class Critique(BaseModel):
    global_score: float = Field(ge=0, le=100)
    rejected_lines: list[Rejection] = Field(default_factory=list)
    signature_moment: str = ""
    revision_directive: str = ""
    identity_score: float = Field(default=0, ge=0, le=100)
    originality_score: float = Field(default=0, ge=0, le=100)
    emotional_truth_score: float = Field(default=0, ge=0, le=100)
    immersion_score: float = Field(default=0, ge=0, le=100)


class QualityVector(BaseModel):
    identity: float = Field(ge=0, le=100)
    originality: float = Field(ge=0, le=100)
    emotional_truth: float = Field(ge=0, le=100)
    language: float = Field(ge=0, le=100)
    flow: float = Field(ge=0, le=100)
    musicality: float = Field(ge=0, le=100)
    voice: float = Field(ge=0, le=100)
    immersion: float = Field(ge=0, le=100)
    replay_value: float = Field(ge=0, le=100)

    @property
    def weighted(self) -> float:
        weights = {
            "identity": 1.25,
            "originality": 1.25,
            "emotional_truth": 1.20,
            "language": 1.0,
            "flow": 1.0,
            "musicality": 1.0,
            "voice": 1.10,
            "immersion": 1.25,
            "replay_value": 1.10,
        }
        values = self.model_dump()
        return sum(values[k] * weights[k] for k in values) / sum(weights.values())

    def passes(self, thresholds: dict[str, float]) -> bool:
        values = self.model_dump()
        return all(values[name] >= threshold for name, threshold in thresholds.items())
