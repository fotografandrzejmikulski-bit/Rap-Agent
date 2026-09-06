from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class CreatorCanon:
    """Durable fictional continuity. Only explicit facts become canon."""

    def __init__(self, path: str = "config/canon.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data = {
                "version": 1,
                "identity_facts": [],
                "people": [],
                "places": [],
                "symbols": [],
                "beliefs": [],
                "open_threads": [],
                "tracks": [],
                "lexical_signatures": [],
                "timeline": [],
            }

    def save(self) -> None:
        self.data["version"] = int(self.data.get("version", 0)) + 1
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def record_track(self, record: dict[str, Any]) -> None:
        payload = {"timestamp": time.time(), **record}
        self.data.setdefault("tracks", []).append(payload)
        self.data.setdefault("timeline", []).append({
            "type": "track",
            "timestamp": payload["timestamp"],
            "title": payload.get("title", ""),
            "event": "utwór powstał",
        })
        self.save()

    def add_thread(self, thread: str) -> None:
        if thread and thread not in self.data.setdefault("open_threads", []):
            self.data["open_threads"].append(thread)
            self.save()

    def snapshot(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.data, ensure_ascii=False))
