from __future__ import annotations

import json
from pathlib import Path

from src.omega.engine import ForgePolicy
from src.omega.models import QualityVector

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    required = [
        "README.md",
        "pyproject.toml",
        "src/omega/models.py",
        "src/omega/psychic.py",
        "src/omega/state_store.py",
        "src/omega/continuity.py",
        "src/omega/retrieval.py",
        "src/omega/engine.py",
        "config/creator.genome.json",
        "config/canon.json",
        "config/quality-gates.json",
        "config/system.json",
        ".github/workflows/omega-wakeup.yml",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing, f"Missing required artifacts: {missing}"
    for config in (ROOT / "config").glob("*.json"):
        json.loads(config.read_text(encoding="utf-8"))
    assert ForgePolicy.THRESHOLDS["identity"] >= 90
    assert ForgePolicy.THRESHOLDS["originality"] >= 90
    print("OMEGA AUDIT: PASS")


if __name__ == "__main__":
    main()
