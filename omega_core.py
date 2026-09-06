"""Ω∞ Rap-Agent core: continuous-state creator engine."""
from __future__ import annotations

import asyncio
import json
import math
import os
import random
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
import numpy as np
from pydantic import BaseModel, Field
from openai import AsyncOpenAI


class EmotionSpace:
    DIMENSIONS = ("anger", "fear", "nostalgia", "pride", "paranoia", "hope", "guilt", "apathy")

    @classmethod
    def baseline(cls) -> np.ndarray:
        return np.array([0.20, 0.40, 0.30, 0.50, 0.60, 0.10, 0.50, 0.40], dtype=float)


class PsychicState(BaseModel):
    timestamp: float
    tensor: dict[str, float]
    wandering_thought: str
    arousal: float = 0.0
    coherence: float = 1.0


class ForgeRequest(BaseModel):
    user_prompt: str = Field(min_length=1)
    mode: str = "absolute"
    temperature: float = Field(default=0.9, ge=0.1, le=1.5)


class TrackResult(BaseModel):
    title: str
    lyrics: list[str]
    dominant_emotion: str
    psychic_state: PsychicState
    memory_path: list[str]
    quality_score: float
    signature_moment: str


@dataclass
class Memory:
    node_id: str
    content: str
    emotion: np.ndarray
    created_at: float
    last_accessed: float
    access_count: int


class SynapticMemory:
    """Persistent weighted associative memory; SQLite is the source of truth."""

    def __init__(self, db_path: str = "data/omega_synapses.sqlite") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph = nx.DiGraph()
        self._init_db()
        self._load()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    node_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS synapses (
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    weight REAL NOT NULL,
                    PRIMARY KEY (source, target),
                    FOREIGN KEY(source) REFERENCES memories(node_id) ON DELETE CASCADE,
                    FOREIGN KEY(target) REFERENCES memories(node_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_memories_last_accessed ON memories(last_accessed);
                """
            )

    def _load(self) -> None:
        with self._connect() as conn:
            for row in conn.execute("SELECT node_id, content, emotion, created_at, last_accessed, access_count FROM memories"):
                self.graph.add_node(
                    row[0],
                    content=row[1],
                    emotion=np.array(json.loads(row[2]), dtype=float),
                    created_at=row[3],
                    last_accessed=row[4],
                    access_count=row[5],
                )
            for source, target, weight in conn.execute("SELECT source, target, weight FROM synapses"):
                self.graph.add_edge(source, target, weight=float(weight))

    def add_memory(self, content: str, emotion: np.ndarray, related: Iterable[str] = ()) -> str:
        node_id = f"mem_{int(time.time_ns())}_{random.randrange(10_000):04d}"
        now = time.time()
        payload = json.dumps(np.asarray(emotion, dtype=float).tolist())
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO memories(node_id, content, emotion, created_at, last_accessed, access_count) VALUES (?, ?, ?, ?, ?, 1)",
                (node_id, content, payload, now, now),
            )
            for target in related:
                if self.graph.has_node(target):
                    self._upsert_synapse(conn, node_id, target, 1.0)
                    self._upsert_synapse(conn, target, node_id, 0.5)
        self.graph.add_node(
            node_id,
            content=content,
            emotion=np.asarray(emotion, dtype=float),
            created_at=now,
            last_accessed=now,
            access_count=1,
        )
        for target in related:
            if self.graph.has_node(target):
                self.graph.add_edge(node_id, target, weight=1.0)
                self.graph.add_edge(target, node_id, weight=0.5)
        return node_id

    @staticmethod
    def _upsert_synapse(conn: sqlite3.Connection, source: str, target: str, weight: float) -> None:
        conn.execute(
            "INSERT INTO synapses(source, target, weight) VALUES (?, ?, ?) ON CONFLICT(source, target) DO UPDATE SET weight=excluded.weight",
            (source, target, weight),
        )

    def reinforce(self, source: str, target: str, amount: float = 0.08) -> None:
        if not (self.graph.has_node(source) and self.graph.has_node(target)):
            return
        current = float(self.graph.get_edge_data(source, target, {}).get("weight", 0.25))
        updated = min(5.0, current + amount)
        self.graph.add_edge(source, target, weight=updated)
        with self._connect() as conn:
            self._upsert_synapse(conn, source, target, updated)

    def random_walk(self, steps: int = 3, start: str | None = None) -> list[str]:
        if not self.graph:
            return []
        current = start if start and self.graph.has_node(start) else random.choice(list(self.graph.nodes))
        path: list[str] = []
        for _ in range(max(1, steps)):
            path.append(current)
            neighbors = list(self.graph.successors(current))
            if not neighbors:
                break
            weights = np.array([max(0.001, self.graph[current][n]["weight"]) for n in neighbors], dtype=float)
            weights /= weights.sum()
            nxt = str(np.random.choice(neighbors, p=weights))
            self.reinforce(current, nxt)
            current = nxt
        now = time.time()
        with self._connect() as conn:
            for node_id in path:
                conn.execute(
                    "UPDATE memories SET last_accessed=?, access_count=access_count+1 WHERE node_id=?",
                    (now, node_id),
                )
        for node_id in path:
            self.graph.nodes[node_id]["last_accessed"] = now
            self.graph.nodes[node_id]["access_count"] += 1
        return path

    def render_path(self, path: list[str]) -> str:
        return " -> ".join(self.graph.nodes[n]["content"] for n in path if self.graph.has_node(n))


class CreatorState:
    def __init__(self) -> None:
        self.tensor = EmotionSpace.baseline()
        self.wandering_thought = "Pustka po ostatniej myśli."
        self.last_update = time.time()
        self.arousal = 0.0
        self.coherence = 1.0
        self.lock = asyncio.Lock()

    async def drift(self, memory: SynapticMemory) -> None:
        async with self.lock:
            now = time.time()
            dt = max(0.1, now - self.last_update)
            baseline = EmotionSpace.baseline()
            decay = 1.0 - math.exp(-0.035 * dt)
            noise_scale = min(0.05, 0.008 * math.sqrt(dt))
            noise = np.random.normal(0.0, noise_scale, len(baseline))
            self.tensor = np.clip(self.tensor + (baseline - self.tensor) * decay + noise, 0.0, 1.0)
            self.arousal = float(np.clip(0.75 * self.arousal + 0.25 * np.mean(self.tensor), 0.0, 1.0))
            self.coherence = float(np.clip(0.92 * self.coherence + 0.08 * (1.0 - np.std(self.tensor)), 0.0, 1.0))
            self.last_update = now
            path = memory.random_walk(steps=2)
            if path:
                self.wandering_thought = memory.render_path(path)

    async def apply_stimulus(self, stimulus: str) -> None:
        # Deterministic-ish lexical perturbation rather than an arbitrary positive boost.
        text = stimulus.lower()
        delta = np.zeros(len(EmotionSpace.DIMENSIONS), dtype=float)
        lexicon = {
            "anger": ("wkurw", "złość", "gniew", "wściek", "zemst"),
            "fear": ("strach", "lęk", "boję", "panik"),
            "nostalgia": ("dom", "dzieci", "wspomn", "kiedyś", "matka", "ojciec"),
            "pride": ("duma", "zwycię", "sukces", "honor"),
            "paranoia": ("system", "polic", "szpieg", "podsłuch", "kłam"),
            "hope": ("jutro", "nadzie", "zmiana", "wyjście", "wolność"),
            "guilt": ("wina", "żał", "przepras", "krzywd"),
            "apathy": ("nic", "pusto", "oboję", "bez sens"),
        }
        for i, dim in enumerate(EmotionSpace.DIMENSIONS):
            delta[i] = sum(0.035 for token in lexicon[dim] if token in text)
        self.tensor = np.clip(self.tensor + delta, 0.0, 1.0)
        self.arousal = float(np.clip(self.arousal + np.linalg.norm(delta) * 2.0, 0.0, 1.0))

    def snapshot(self) -> PsychicState:
        return PsychicState(
            timestamp=time.time(),
            tensor=dict(zip(EmotionSpace.DIMENSIONS, self.tensor.tolist())),
            wandering_thought=self.wandering_thought,
            arousal=self.arousal,
            coherence=self.coherence,
        )


class LLM:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("OMEGA_MODEL", "gpt-4.1")

    @staticmethod
    def system_prompt() -> str:
        return """
Jesteś Ω∞ — autonomicznym fikcyjnym twórcą polskiego rapu. Nie imitujesz istniejących artystów.
Masz własny Creator Genome: Lubelszczyzna, doświadczenie Słowacji i Śląska, doświadczenie więzienne,
charakterystyczny dorosły niski/chropowaty głos oraz język rozwijający się z biografii.
Piszesz przede wszystkim po polsku. Surowość jest dozwolona, ale każde mocne słowo musi być funkcjonalne.
Priorytety: tożsamość > prawda emocjonalna > oryginalność > narracja > flow > muzykalność > efekt.
Unikaj generycznych metafor, sztucznego slangu, pustego patosu i fraz brzmiących jak model językowy.
Odbiorca ma mieć wrażenie wejścia do głowy konkretnego człowieka.
Nie twórz bezpodstawnych deklaracji o prawdziwych doświadczeniach realnej osoby; to fikcyjna persona.
""".strip()

    async def generate(self, state: PsychicState, memory: str, request: ForgeRequest) -> list[str]:
        emotion_json = json.dumps(state.tensor, ensure_ascii=False)
        prompt = f"""
AKTUALNY STAN PSYCHICZNY:
{emotion_json}
AROUSAL={state.arousal:.3f}; COHERENCE={state.coherence:.3f}

BŁĄDZĄCA MYŚL:
{memory or state.wandering_thought}

BODZIEC UŻYTKOWNIKA:
{request.user_prompt}

Napisz kompletny tekst utworu. Najpierw wybierz punkt widzenia, osobisty detal i dominującą emocję.
Nie ujawniaj procesu rozumowania. Zwróć tylko gotowe wersy, jeden wers na linię.
Pozwól strukturze być nieregularnej, jeśli zwiększa autentyczność.
"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=request.temperature,
        )
        text = (response.choices[0].message.content or "").strip()
        return [line.strip() for line in text.splitlines() if line.strip()]

    async def critique(self, lines: list[str], state: PsychicState) -> dict[str, Any]:
        numbered = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))
        prompt = f"""
Oceń tekst bez litości. Stan psychiczny: {json.dumps(state.tensor, ensure_ascii=False)}

TEKST:
{numbered}

Zwróć JSON z polami:
{{
  "global_score": 0-100,
  "rejected_lines": [{{"line": 1, "reason": "..."}}],
  "signature_moment": "...",
  "revision_directive": "..."
}}
Odrzucaj banał, imitację, sztuczną uliczność, wymuszone rymy, nadmiar objaśnień i frazy bez indywidualnego DNA.
"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Jesteś adversarialnym redaktorem Ω∞. Zwracaj wyłącznie poprawny JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "{}"
        return json.loads(raw)

    async def reconstruct(self, lines: list[str], critique: dict[str, Any], request: ForgeRequest) -> list[str]:
        rejected = {int(item["line"]): item["reason"] for item in critique.get("rejected_lines", [])}
        material = "\n".join(
            f"{i+1}: {'[ZACHOWAJ]' if i+1 not in rejected else '[ODBUDUJ: ' + rejected[i+1] + ']'} {line}"
            for i, line in enumerate(lines)
        )
        prompt = f"""
Przebuduj tekst zgodnie z krytyką. Zachowaj sens mocnych wersów, ale napraw słabe.
Nie zwiększaj sztucznie liczby przekleństw. Nie kopiuj żadnego istniejącego artysty.

{material}

DYREKTYWA:
{critique.get('revision_directive', '')}

Zwróć wyłącznie wersy, jeden na linię.
"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=max(0.65, request.temperature - 0.05),
        )
        text = (response.choices[0].message.content or "").strip()
        return [line.strip() for line in text.splitlines() if line.strip()]


class OmegaForge:
    def __init__(self, memory: SynapticMemory, state: CreatorState, llm: LLM) -> None:
        self.memory = memory
        self.state = state
        self.llm = llm

    async def forge(self, request: ForgeRequest) -> TrackResult:
        await self.state.drift(self.memory)
        await self.state.apply_stimulus(request.user_prompt)
        state = self.state.snapshot()
        path = self.memory.random_walk(steps=3)
        thought = self.memory.render_path(path) or state.wandering_thought

        lines = await self.llm.generate(state, thought, request)
        best_score = 0.0
        signature = ""
        for _ in range(4):
            critique = await self.llm.critique(lines, state)
            score = float(critique.get("global_score", 0.0))
            signature = str(critique.get("signature_moment", ""))
            best_score = max(best_score, score)
            if score >= 94 and not critique.get("rejected_lines"):
                break
            lines = await self.llm.reconstruct(lines, critique, request)
            if not lines:
                raise RuntimeError("Reconstruction produced empty lyrics")

        related = path[-3:]
        node_id = self.memory.add_memory(
            content=f"Utwór: {request.user_prompt}\nFragment: {lines[0] if lines else ''}",
            emotion=self.state.tensor,
            related=related,
        )
        dominant = EmotionSpace.DIMENSIONS[int(np.argmax(self.state.tensor))]
        title = self._derive_title(lines, dominant)
        return TrackResult(
            title=title,
            lyrics=lines,
            dominant_emotion=dominant,
            psychic_state=self.state.snapshot(),
            memory_path=path + [node_id],
            quality_score=best_score,
            signature_moment=signature or (lines[len(lines)//2] if lines else ""),
        )

    @staticmethod
    def _derive_title(lines: list[str], dominant: str) -> str:
        if not lines:
            return f"Ω∞ — {dominant}"
        seed = lines[0].strip(" .,!?:;-–—\"")
        words = seed.split()
        return (" ".join(words[:6]) or f"Ω∞ — {dominant}").capitalize()
