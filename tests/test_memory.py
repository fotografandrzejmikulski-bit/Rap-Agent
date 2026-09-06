from pathlib import Path

from src.omega.memory import AssociativeMemory


def test_associative_memory_round_trip(tmp_path: Path) -> None:
    mem = AssociativeMemory(str(tmp_path / "omega.sqlite"))
    first = mem.add("zimny korytarz", [0.8, 0.1, 0.2, 0.3, 0.7, 0.0, 0.2, 0.5])
    second = mem.add("stary dom", [0.1, 0.2, 0.9, 0.4, 0.1, 0.2, 0.4, 0.3], related=[first])
    assert mem.exists(first)
    assert mem.exists(second)
    ranked = mem.spread([0.75, 0.1, 0.25, 0.2, 0.7, 0.0, 0.2, 0.5])
    assert ranked
    assert ranked[0]["id"] == first


def test_memory_confidence_is_bounded(tmp_path: Path) -> None:
    mem = AssociativeMemory(str(tmp_path / "omega.sqlite"))
    node = mem.add("test", [0.0] * 8, confidence=3.0)
    item = next(x for x in mem.recent() if x["id"] == node)
    assert item["confidence"] == 1.0
