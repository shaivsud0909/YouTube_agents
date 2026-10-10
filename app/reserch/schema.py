
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    region: str = Field(
        default="US",
        min_length=2,
        max_length=2,
        description="Region code (ISO 3166-1 alpha-2) for filtering results.",
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=2,
        description="Language code (ISO 639-1) for filtering results.",
    )
    max_results: int = Field(default=10, ge=1, le=50)


class ResearchSource(BaseModel):
    source_type: Literal["web", "youtube"]
    title: str
    url: HttpUrl
    content: str = ""
    published_at: datetime | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )


class ResearchResult(BaseModel):
    topic: str
    sources: list[ResearchSource] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
