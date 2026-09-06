import json
from pathlib import Path


def test_creator_genome_has_identity_invariants() -> None:
    data = json.loads(Path("config/creator.genome.json").read_text(encoding="utf-8"))
    assert data["identity"]["fictional"] is True
    assert data["identity"]["language"] == "pl-PL"
    assert data["biography"]["origin"] == "Lubelszczyzna"
    assert data["originality"]["imitation_forbidden"] is True
    assert data["continuity"]["canon_required"] is True
