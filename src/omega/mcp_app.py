"""Official MCP application surface for Ω∞ Rap-Agent."""
from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from omega.runtime import OmegaRuntime

runtime = OmegaRuntime.build()

mcp = FastMCP(
    "Omega Rap-Agent",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    instructions=(
        "You are connected to the canonical Ω∞ Polish rap creator runtime. "
        "Use omega_state before major creative operations when continuity matters. "
        "Never imitate a living artist. Preserve Creator Genome and Canon."
    ),
)


@mcp.tool()
def omega_forge(prompt: str, temperature: float = 0.85) -> dict:
    """Create a Polish rap track through the persistent Ω∞ forge."""
    # The canonical runtime/orchestrator owns generation and state transitions.
    from omega.orchestrator import OmegaOrchestrator

    orchestrator = OmegaOrchestrator()
    # MCP tools are synchronous; run the async forge to completion.
    import asyncio

    artifact = asyncio.run(orchestrator.forge(prompt))
    return {
        "request_id": artifact.request_id,
        "title": artifact.title,
        "lyrics": artifact.lyrics,
        "quality": artifact.quality.model_dump(),
        "critique": artifact.critique.model_dump(),
        "signature_moment": artifact.signature_moment,
        "psychic_state": artifact.psychic_state,
        "memory_path": artifact.memory_path,
    }


@mcp.tool()
def omega_state() -> dict:
    """Return the current durable psychic state and creator continuity snapshot."""
    return {
        "psychic_state": runtime.psychic.snapshot(),
        "continuity": runtime.continuity.recent("", limit=20),
        "canon": runtime.canon.snapshot(),
    }


@mcp.tool()
def omega_memory_stats() -> dict:
    """Return durable associative-memory statistics."""
    return {"database": os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite")}


def main() -> None:
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        stateless_http=True,
        json_response=True,
    )


if __name__ == "__main__":
    main()
