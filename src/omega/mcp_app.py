"""Official MCP application surface for Ω∞ Rap-Agent.

Uses the MCP Python SDK when installed. The application delegates all stateful
work to the canonical OmegaRuntime so MCP clients cannot create a second brain.
"""
from __future__ import annotations

import os

from omega.runtime import OmegaRuntime

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "MCP SDK is required. Install the project's MCP extra/dependencies."
    ) from exc

runtime = OmegaRuntime(
    db_path=os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite")
)

mcp = FastMCP(
    "Omega Rap-Agent",
    instructions=(
        "You are connected to the canonical Ω∞ Polish rap creator runtime. "
        "Use omega_state before major creative operations when continuity matters. "
        "Never imitate a living artist. Preserve Creator Genome and Canon."
    ),
)


@mcp.tool()
def omega_forge(prompt: str, mode: str = "absolute", temperature: float = 0.85) -> dict:
    """Create a complete Polish rap track through the persistent Ω∞ forge."""
    return runtime.forge(prompt, mode, temperature)


@mcp.tool()
def omega_state() -> dict:
    """Return the current durable psychic state and creator continuity snapshot."""
    return runtime.state()


@mcp.tool()
def omega_memory_stats() -> dict:
    """Return durable associative-memory statistics."""
    return runtime.memory_stats()


def main() -> None:
    # Streamable HTTP is suitable for remote ChatGPT MCP connections.
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
