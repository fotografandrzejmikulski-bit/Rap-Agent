from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_system() -> dict[str, Any]:
    return load_json("config/system.json")


def load_genome() -> dict[str, Any]:
    return load_json("config/creator.genome.json")


def load_quality() -> dict[str, Any]:
    return load_json("config/quality-gates.json")
