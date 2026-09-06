"""Remote MCP adapter for the Ω∞ Rap-Agent runtime.

The server exposes the canonical forge/state/memory operations without duplicating
business logic. The transport is intentionally thin: runtime policy and creator
state remain owned by the core package.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from omega.runtime import OmegaRuntime

app = FastAPI(title="Ω∞ Rap-Agent MCP Bridge", version="1.0.0")
runtime = OmegaRuntime(
    db_path=os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite")
)


class ForgeInput(BaseModel):
    prompt: str = Field(min_length=1)
    mode: str = "absolute"
    temperature: float = Field(default=0.85, ge=0.1, le=1.2)


@app.get("/health")
def health() -> dict[str, Any]:
    return runtime.health()


@app.get("/tools")
def tools() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": "omega_forge",
                "description": "Create a Polish rap track using the persistent Ω∞ creator state.",
                "input_schema": ForgeInput.model_json_schema(),
            },
            {
                "name": "omega_state",
                "description": "Read the current persistent psychic state and wandering thought.",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "omega_memory_stats",
                "description": "Read persistent memory graph statistics.",
                "input_schema": {"type": "object", "properties": {}},
            },
        ]
    }


@app.post("/call/omega_forge")
def omega_forge(payload: ForgeInput) -> dict[str, Any]:
    return runtime.forge(payload.prompt, payload.mode, payload.temperature)


@app.post("/call/omega_state")
def omega_state() -> dict[str, Any]:
    return runtime.state()


@app.post("/call/omega_memory_stats")
def omega_memory_stats() -> dict[str, Any]:
    return runtime.memory_stats()


# MCP-compatible Streamable HTTP endpoint can be added by mounting the official
# MCP ASGI application once the deployment environment installs the MCP SDK.
# The REST facade above is retained for health checks and OpenAPI tooling.
