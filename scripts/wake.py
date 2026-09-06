from __future__ import annotations

import asyncio
import os

from src.omega.runtime import OmegaRuntime


async def main() -> None:
    runtime = OmegaRuntime.build()
    ticks = int(os.environ.get("OMEGA_WAKE_TICKS", "1"))
    await runtime.wake(max(1, min(ticks, 60)))
    print("[Ω∞] wake complete")
    print(runtime.psychic.snapshot())


if __name__ == "__main__":
    asyncio.run(main())
