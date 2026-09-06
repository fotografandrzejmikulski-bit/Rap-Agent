"""FastAPI bridge for the Ω∞ creator core."""
from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, HTTPException

from omega_core import CreatorState, ForgeRequest, LLM, OmegaForge, PsychicState, SynapticMemory

app = FastAPI(title="Ω∞ Singularity Rap-Agent", version="4.0.0")

memory = SynapticMemory(os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite"))
state = CreatorState()
llm = LLM()
forge = OmegaForge(memory, state, llm)

_consciousness_task: asyncio.Task[None] | None = None


async def _consciousness_loop() -> None:
    while True:
        try:
            await state.drift(memory)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Background consciousness must not kill the API process.
            pass
        await asyncio.sleep(float(os.environ.get("OMEGA_DRIFT_SECONDS", "10")))


@app.on_event("startup")
async def startup() -> None:
    global _consciousness_task
    if _consciousness_task is None or _consciousness_task.done():
        _consciousness_task = asyncio.create_task(_consciousness_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    global _consciousness_task
    if _consciousness_task:
        _consciousness_task.cancel()
        await asyncio.gather(_consciousness_task, return_exceptions=True)
        _consciousness_task = None


@app.get("/health")
async def health() -> dict[str, object]:
    return {"status": "ONLINE", "mode": "OMEGA_SINGULARITY", "consciousness": _consciousness_task is not None}


@app.get("/state", response_model=PsychicState)
async def current_state() -> PsychicState:
    return state.snapshot()


@app.post("/forge")
async def forge_endpoint(request: ForgeRequest):
    try:
        result = await forge.forge(request)
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ω∞ forge failure: {exc}") from exc


@app.get("/memory/stats")
async def memory_stats() -> dict[str, int]:
    return {"nodes": memory.graph.number_of_nodes(), "synapses": memory.graph.number_of_edges()}
