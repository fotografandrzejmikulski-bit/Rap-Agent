"""Production FastAPI bridge for the canonical Ω∞ runtime."""
from __future__ import annotations

import asyncio
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.omega.orchestrator import OmegaOrchestrator
from src.omega.runtime import OmegaRuntime

app = FastAPI(title="Ω∞ Singularity Rap-Agent", version="6.0.0")
runtime = OmegaRuntime.build()
forge = OmegaOrchestrator(
    db_path=os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite"),
    canon_path=os.environ.get("OMEGA_CANON_PATH", "config/canon.json"),
)
_consciousness_task: asyncio.Task[None] | None = None


class ForgeInput(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    max_cycles: int = Field(default=12, ge=1, le=12)


@app.on_event("startup")
async def startup() -> None:
    global _consciousness_task
    if _consciousness_task is None or _consciousness_task.done():
        async def loop() -> None:
            while True:
                try:
                    await runtime.wake(1)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass
                await asyncio.sleep(float(os.environ.get("OMEGA_DRIFT_SECONDS", "60")))
        _consciousness_task = asyncio.create_task(loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    global _consciousness_task
    if _consciousness_task:
        _consciousness_task.cancel()
        await asyncio.gather(_consciousness_task, return_exceptions=True)
        _consciousness_task = None


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ONLINE",
        "version": "6.0.0",
        "runtime": "canonical",
        "consciousness_loop": _consciousness_task is not None,
        "db": os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite"),
    }


@app.get("/state")
async def state() -> dict[str, Any]:
    return runtime.psychic.snapshot()


@app.get("/canon")
async def canon() -> dict[str, Any]:
    return runtime.canon.snapshot()


@app.get("/events")
async def events(limit: int = 50) -> list[dict[str, Any]]:
    return runtime.continuity.recent(limit=max(1, min(limit, 250)))


@app.post("/wake")
async def wake(ticks: int = 1) -> dict[str, Any]:
    await runtime.wake(max(1, min(ticks, 60)))
    return runtime.psychic.snapshot()


@app.post("/forge")
async def forge_endpoint(payload: ForgeInput, idempotency_key: str | None = Header(default=None)) -> dict[str, Any]:
    if not idempotency_key:
        idempotency_key = os.urandom(16).hex()
    cached = runtime.continuity.load_forge(idempotency_key)
    if cached:
        return {"idempotent_replay": True, **cached}
    try:
        artifact = await forge.forge(payload.prompt, max_cycles=payload.max_cycles)
        result = {
            "request_id": artifact.request_id,
            "title": artifact.title,
            "lyrics": artifact.lyrics,
            "signature_moment": artifact.signature_moment,
            "quality": artifact.quality.model_dump(),
            "critique": artifact.critique.model_dump(),
            "psychic_state": artifact.psychic_state,
            "memory_path": artifact.memory_path,
            "passed": runtime.continuity.load_forge(artifact.request_id) is not None,
        }
        runtime.continuity.save_forge(idempotency_key, payload.prompt, result)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ω∞ forge failure: {exc}") from exc
