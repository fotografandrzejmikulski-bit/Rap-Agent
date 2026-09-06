from __future__ import annotations

from pydantic import BaseModel, Field


class ForgeRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    max_cycles: int = Field(default=12, ge=1, le=12)


class ForgeResponse(BaseModel):
    request_id: str
    title: str
    lyrics: list[str]
    signature_moment: str
    quality: dict[str, float]
    passed: bool
    psychic_state: dict
    memory_path: list[str]
