"""One bounded consciousness tick for GitHub Actions."""
from __future__ import annotations

import asyncio
import os

from omega_core import CreatorState, LLM, SynapticMemory


async def main() -> None:
    memory = SynapticMemory(os.environ.get("OMEGA_DB_PATH", "data/omega_synapses.sqlite"))
    state = CreatorState()
    # Restore a compact state proxy from the latest memory trace when available.
    # A bounded runner cannot remain alive indefinitely; it performs one evolution tick.
    await state.drift(memory)
    print("[Ω∞] wake complete")
    print(state.snapshot().model_dump_json())


if __name__ == "__main__":
    asyncio.run(main())
