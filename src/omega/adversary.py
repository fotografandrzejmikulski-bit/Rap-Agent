from __future__ import annotations

import re
from dataclasses import dataclass


GENERIC = {
    "walka z życiem", "ulica mnie nauczyła", "nikt mnie nie rozumie",
    "wszyscy są fałszywi", "świat jest ciężki", "muszę być silny",
}

RISKY_PATTERNS = [
    r"\bjak .* raper", r"\bw stylu .*\b", r"\bjestem królem\b",
]


@dataclass
class LocalFinding:
    line_id: str
    severity: str
    codes: list[str]
    reason: str


class LocalAdversary:
    """Cheap deterministic pre-filter before expensive model critique."""

    @staticmethod
    def inspect(lines: list[str]) -> list[LocalFinding]:
        findings: list[LocalFinding] = []
        for idx, line in enumerate(lines, start=1):
            text = line.strip()
            lower = text.lower()
            codes: list[str] = []
            if lower in GENERIC:
                codes.append("GENERIC")
            if any(re.search(pattern, lower) for pattern in RISKY_PATTERNS):
                codes.append("STYLE_DEPENDENCY")
            if len(set(lower.split())) <= max(2, len(lower.split()) // 3):
                codes.append("REPETITIVE")
            if text.count("!") >= 3 or text.count("?") >= 3:
                codes.append("PADDING")
            if codes:
                severity = "critical" if "STYLE_DEPENDENCY" in codes else "major"
                findings.append(LocalFinding(f"L{idx}", severity, codes, "deterministic prefilter"))
        return findings
