from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.tools.research_tool import run_research, RESEARCH_TOOL_SCHEMA

research_router = APIRouter()


class ResearchToolInput(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    days_back: int = Field(default=1, ge=1, le=30)
    region: str = Field(default="IN", min_length=2, max_length=2)
    language: str = Field(default="en", min_length=2, max_length=2)
    max_results: int = Field(default=10, ge=1, le=50)


@research_router.get("/schema")
def get_tool_schema():
    """Return the Claude tool schema so callers can register the tool dynamically."""
    return RESEARCH_TOOL_SCHEMA


@research_router.post("/run")
def run_research_endpoint(body: ResearchToolInput):
    try:
        result = run_research(
            topic=body.topic,
            days_back=body.days_back,
            region=body.region,
            language=body.language,
            max_results=body.max_results,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
