from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from .canon import CreatorCanon
from .continuity import ContinuityStore
from .identity import CreatorIdentity
from .models import Critique, QualityVector, Rejection
from .engine import ForgeLedger
from .psychic import PsychicDynamics
from .state_store import StateStore


@dataclass
class ForgeArtifact:
    request_id: str
    title: str
    lyrics: list[str]
    quality: QualityVector
    critique: Critique
    signature_moment: str
    psychic_state: dict[str, Any]
    memory_path: list[str]


class OmegaOrchestrator:
    """Production orchestration: stimulus -> state -> candidate -> adversary -> gate -> canon."""

    def __init__(self, db_path: str = "data/omega_synapses.sqlite", canon_path: str = "config/canon.json") -> None:
        store = StateStore(db_path)
        self.state = PsychicDynamics(store)
        self.continuity = ContinuityStore(db_path)
        self.canon = CreatorCanon(canon_path)
        self.identity = CreatorIdentity()
        self.ledger = ForgeLedger(self.continuity)
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("OMEGA_MODEL", "gpt-4.1")

    def _system(self) -> str:
        return (
            "Jesteś Ω∞ — fikcyjnym, autonomicznym twórcą polskiego rapu.\n"
            "Nie imitujesz konkretnych artystów i nie tworzysz podszycia pod realną osobę.\n"
            "Tożsamość, biografia, język, głos, psychologia, pamięć i ewolucja są spójne.\n"
            "Polski jest językiem podstawowym. Surowy język jest dozwolony funkcjonalnie.\n"
            "Najpierw znaczenie i człowiek, potem technika. Odbiorca ma wejść do głowy narratora.\n"
            f"CANON: {json.dumps(self.canon.snapshot(), ensure_ascii=False)}\n"
            f"GENOME: {self.identity.prompt_fragment()}"
        )

    async def _generate(self, prompt: str, temperature: float) -> list[str]:
        state = self.state.snapshot()
        payload = (
            f"STAN: {json.dumps(state, ensure_ascii=False)}\n"
            f"BODZIEC: {prompt}\n"
            "Wytwórz kandydat na kompletny utwór. Dobierz punkt widzenia, konflikt i mikrodetal. "
            "Struktura ma wynikać z utworu. Zwróć wyłącznie wersy, jeden na linię."
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self._system()}, {"role": "user", "content": payload}],
            temperature=temperature,
        )
        text = (response.choices[0].message.content or "").strip()
        return [line.strip() for line in text.splitlines() if line.strip()]

    async def _critique(self, lines: list[str]) -> Critique:
        numbered = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))
        prompt = f"""
Zostań bezlitosnym zespołem redakcyjnym Ω∞. Oceń każdą linię i cały utwór.
Wykryj banał, sztuczną uliczność, imitację, logikę kalki, wymuszone rymy,
powtarzalność, słabą zgodność z DNA, brak mikrodetali i brak napięcia.
Wynik ma być poprawnym JSON zgodnym ze schematem:
{{
  "global_score": 0-100,
  "rejected_lines": [
    {{"line_id":"L1","severity":"critical|major|minor","reason_codes":["BANAL","IMITATION","GENERIC","RHYME","VOICE","DNA","IMMERSION"],"reason":"...","replacement_strategy":"REWRITE|RECONTEXTUALIZE|DELETE|MERGE","preserve":["..."]}}
  ],
  "signature_moment":"...",
  "revision_directive":"...",
  "identity_score":0-100,
  "originality_score":0-100,
  "emotional_truth_score":0-100,
  "immersion_score":0-100
}}

TEKST:
{numbered}
"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Jesteś adwersarialnym redaktorem. Zwracaj wyłącznie JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content or "{}")
        return Critique.model_validate(data)

    async def _rebuild(self, lines: list[str], critique: Critique) -> list[str]:
        rejected = {r.line_id: r for r in critique.rejected_lines}
        source = "\n".join(
            f"L{i+1} {'[NAPRAW]' if f'L{i+1}' in rejected else '[ZACHOWAJ]'} {line}"
            for i, line in enumerate(lines)
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system()},
                {"role": "user", "content": (
                    "Przebuduj tekst na podstawie krytyki. Zachowaj sens i dobre mikrodetale. "
                    "Usuń kalki. Nie imituj żadnego artysty. Zwróć wyłącznie wersy.\n\n"
                    + source + "\n\nDYREKTYWA:\n" + critique.revision_directive
                )},
            ],
            temperature=0.72,
        )
        text = (response.choices[0].message.content or "").strip()
        return [line.strip() for line in text.splitlines() if line.strip()]

    @staticmethod
    def _quality(critique: Critique, lines: list[str]) -> QualityVector:
        # Deterministic fallback dimensions until a dedicated judge model is added.
        base = critique.global_score
        return QualityVector(
            identity=critique.identity_score,
            originality=critique.originality_score,
            emotional_truth=critique.emotional_truth_score,
            language=min(100.0, base + (2.0 if lines else 0.0)),
            flow=base,
            musicality=base,
            voice=min(100.0, (critique.identity_score + critique.immersion_score) / 2),
            immersion=critique.immersion_score,
            replay_value=min(100.0, (base + critique.originality_score) / 2),
        )

    async def forge(self, prompt: str, max_cycles: int = 12) -> ForgeArtifact:
        request_id = str(uuid.uuid4())
        await self.state.drift(self.state.store)  # elapsed + stochastic state evolution
        stimulus = self.state.apply_stimulus(prompt)
        self.continuity.append("stimulus.received", {"request_id": request_id, "prompt": prompt, "delta": stimulus})

        lines = await self._generate(prompt, temperature=0.9)
        final_critique = Critique(global_score=0)
        quality = QualityVector(*([0.0] * 9))  # overwritten after first critique

        for _ in range(max_cycles):
            final_critique = await self._critique(lines)
            quality = self._quality(final_critique, lines)
            passed, _ = self.ledger.continuity.recent("forge.finalized", limit=0), []
            hard_pass, _failures = __import__("src.omega.engine", fromlist=["ForgePolicy"]).ForgePolicy.validate(quality)
            if hard_pass and not final_critique.rejected_lines:
                break
            lines = await self._rebuild(lines, final_critique)

        record = self.ledger.record(prompt, lines, final_critique, quality)
        passed = bool(record["passed"])
        if passed:
            self.canon.record_track({
                "title": f"Omega-{request_id[:8]}",
                "request_id": request_id,
                "artifact_hash": record["artifact_hash"],
                "signature_moment": final_critique.signature_moment,
                "dominant_emotion": max(self.state.tensor.tolist()),
            })
            self.continuity.append("canon.track_added", {"request_id": request_id, "hash": record["artifact_hash"]})

        return ForgeArtifact(
            request_id=request_id,
            title=f"Omega-{request_id[:8]}",
            lyrics=lines,
            quality=quality,
            critique=final_critique,
            signature_moment=final_critique.signature_moment,
            psychic_state=self.state.snapshot(),
            memory_path=[],
        )
