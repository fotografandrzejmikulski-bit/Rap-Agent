from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from .continuity import ContinuityStore
from .models import Critique, QualityVector


class ArtifactHasher:
    @staticmethod
    def text(lines: list[str]) -> str:
        payload = "\n".join(line.strip() for line in lines)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ForgePolicy:
    """Hard production policy: identity and originality are veto dimensions."""

    THRESHOLDS = {
        "identity": 90.0,
        "originality": 90.0,
        "emotional_truth": 88.0,
        "language": 86.0,
        "flow": 86.0,
        "musicality": 86.0,
        "voice": 88.0,
        "immersion": 90.0,
        "replay_value": 88.0,
    }

    @classmethod
    def validate(cls, quality: QualityVector) -> tuple[bool, list[str]]:
        values = quality.model_dump()
        failures = [name for name, threshold in cls.THRESHOLDS.items() if values[name] < threshold]
        return not failures and quality.weighted >= 89.0, failures


class ForgeLedger:
    """Durable evidence that a track passed through the forge."""

    def __init__(self, continuity: ContinuityStore) -> None:
        self.continuity = continuity

    def record(self, prompt: str, lines: list[str], critique: Critique, quality: QualityVector) -> dict[str, Any]:
        request_id = str(uuid.uuid4())
        artifact_hash = ArtifactHasher.text(lines)
        passed, failures = ForgePolicy.validate(quality)
        result = {
            "request_id": request_id,
            "artifact_hash": artifact_hash,
            "passed": passed,
            "failures": failures,
            "quality": quality.model_dump(),
            "critique": critique.model_dump(),
        }
        self.continuity.save_forge(request_id, prompt, result)
        self.continuity.append("forge.finalized" if passed else "forge.rejected", result)
        return result
