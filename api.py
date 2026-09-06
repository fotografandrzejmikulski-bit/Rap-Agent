"""Production FastAPI bridge for the canonical Ω∞ runtime."""
from __future__ import annotations

import asyncio
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.omega.health import RuntimeHealth
from src.omega.orchestrator import OmegaOrchestrator
from src.omega.runtime import OmegaRuntime

app = FastAPI(title="Ω∞ Singularity Rap-Agent", version="6.3.0")
runtime = OmegaRuntime.build()
forge = OmegaOrchestrator(
    db_path=os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite"),
    canon_path=os.environ.get("OMEGA_CANON_PATH", "config/canon.json"),
)
health = RuntimeHealth(runtime.psychic, runtime.continuity, runtime.canon)
_consciousness_task: asyncio.Task[None] | None = None


class ForgeInput(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    max_cycles: int = Field(default=12, ge=1, le=12)


@app.on_event("startup")
async def startup() -> None:
    global _consciousness_task
    if _consciousness_task is not None and not _consciousness_task.done():
        return

    async def loop() -> None:
        while True:
            try:
                await runtime.wake(1)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                runtime.continuity.append("runtime.error", {"type": type(exc).__name__, "message": str(exc)[:500]})
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
async def health_endpoint() -> dict[str, Any]:
    return health.snapshot()


@app.get("/state")
async def state_endpoint() -> dict[str, Any]:
    return runtime.psychic.snapshot()


@app.get("/canon")
async def canon_endpoint() -> dict[str, Any]:
    return runtime.canon.snapshot()


@app.get("/events")
async def events_endpoint(limit: int = 50) -> list[dict[str, Any]]:
    return runtime.continuity.recent(limit=max(1, min(limit, 250)))


@app.post("/wake")
async def wake_endpoint(ticks: int = 1) -> dict[str, Any]:
    await runtime.wake(max(1, min(ticks, 60)))
    return runtime.psychic.snapshot()


@app.post("/forge")
async def forge_endpoint(payload: ForgeInput, idempotency_key: str | None = Header(default=None)) -> dict[str, Any]:
    key = idempotency_key or os.urandom(16).hex()
    cached = runtime.continuity.load_forge(key)
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
            "passed": False,
        }
        runtime.continuity.save_forge(key, payload.prompt, result)
        result["passed"] = runtime.continuity.load_forge(artifact.request_id) is not None
        return result
    except Exception as exc:
        runtime.continuity.append("forge.error", {"message": str(exc)[:1000]})
        raise HTTPException(status_code=500, detail="Ω∞ forge failure") from exc
