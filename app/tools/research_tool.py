import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from core.logs import logger
from app.rag.ingestion import ResearchIngestion
from app.reserch.schema import ResearchRequest
from app.reserch.scrap import ScrapingResearch
from app.reserch.transcript import TranscriptResearch


OUTPUT_DIR = Path("data/research")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Claude tool schema — pass this in your tools=[] list when calling the API
RESEARCH_TOOL_SCHEMA: dict[str, Any] = {
    "name": "run_research",
    "description": (
        "Collect web articles and YouTube video transcripts about a topic, "
        "chunk them, generate embeddings, and store them in the vector database "
        "so they can be retrieved for RAG. Call this whenever you need fresh "
        "sources before answering a question."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The research topic or question (3–500 characters).",
            },
            "days_back": {
                "type": "integer",
                "description": "How many days back to search for content (default: 1).",
                "default": 1,
            },
            "region": {
                "type": "string",
                "description": "ISO 3166-1 alpha-2 region code, e.g. 'IN', 'US' (default: 'IN').",
                "default": "IN",
            },
            "language": {
                "type": "string",
                "description": "ISO 639-1 language code, e.g. 'en', 'hi' (default: 'en').",
                "default": "en",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of sources to fetch (1–50, default: 10).",
                "default": 10,
            },
        },
        "required": ["topic"],
    },
}


def run_research(
    topic: str,
    days_back: int = 1,
    region: str = "IN",
    language: str = "en",
    max_results: int = 10,
) -> dict[str, Any]:
    """Execute the full research + ingestion pipeline and return a summary."""

    request = ResearchRequest(
        topic=topic,
        date=datetime.now(timezone.utc) - timedelta(days=days_back),
        region=region,
        language=language,
        max_results=max_results,
    )

    all_sources = []
    errors: list[str] = []

    try:
        logger.info("Tool: starting web research for '%s'", topic)
        web_result = ScrapingResearch().research(request)
        all_sources.extend(web_result.sources)
        errors.extend(web_result.errors)
    except Exception as exc:
        logger.exception("Tool: web research failed")
        errors.append(f"Web research failed: {exc}")

    try:
        logger.info("Tool: starting YouTube research for '%s'", topic)
        yt_result = TranscriptResearch().research(request)
        all_sources.extend(yt_result.sources)
        errors.extend(yt_result.errors)
    except Exception as exc:
        logger.exception("Tool: YouTube research failed")
        errors.append(f"YouTube research failed: {exc}")

    result = {
        "topic": topic,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_sources": len(all_sources),
        "sources": [s.model_dump(mode="json") for s in all_sources],
        "errors": errors,
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"research_{timestamp}.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    chunks_stored = 0
    try:
        chunks_stored = ResearchIngestion().ingest(output_file)
    except Exception as exc:
        logger.exception("Tool: RAG ingestion failed")
        errors.append(f"RAG ingestion failed: {exc}")

    return {
        "status": "completed",
        "topic": topic,
        "sources_collected": len(all_sources),
        "chunks_stored": chunks_stored,
        "output_file": str(output_file),
        "errors": errors,
    }


def dispatch_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Route a tool_use block from the Claude API to the right function."""
    if tool_name == "run_research":
        result = run_research(**tool_input)
        return json.dumps(result)
    raise ValueError(f"Unknown tool: {tool_name}")
