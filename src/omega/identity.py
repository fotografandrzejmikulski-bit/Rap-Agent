from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CreatorIdentity:
    """Loads immutable identity constraints plus evolvable creative traits."""

    def __init__(self, path: str = "config/creator.genome.json") -> None:
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    @property
    def immutable(self) -> dict[str, Any]:
        return self.data.get("immutable_identity", self.data.get("identity", {}))

    @property
    def language_rules(self) -> dict[str, Any]:
        return self.data.get("language", {})

    @property
    def voice(self) -> dict[str, Any]:
        return self.data.get("voice", {})

    @property
    def artistic_rules(self) -> dict[str, Any]:
        return self.data.get("artistic", self.data.get("creative_rules", {}))

    def prompt_fragment(self) -> str:
        return json.dumps(
            {
                "immutable_identity": self.immutable,
                "language": self.language_rules,
                "voice": self.voice,
                "artistic": self.artistic_rules,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
