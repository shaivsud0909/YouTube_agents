import json
from typing import Any

from core.logs import logger
from app.rag.retriver import ResearchRetriever


RETRIEVER_TOOL_SCHEMA: dict[str, Any] = {
    "name": "retrieve_context",
    "description": (
        "Search the vector database for chunks relevant to a topic or question. "
        "Returns the top matching text chunks with their metadata and similarity scores. "
        "Call this before answering a question to ground your response in stored research."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic or question to search for in the vector database.",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of chunks to retrieve (1–20, default: 5).",
                "default": 5,
            },
        },
        "required": ["topic"],
    },
}


def retrieve_context(topic: str, top_k: int = 5) -> dict[str, Any]:
    """Retrieve relevant chunks from the vector DB for the given topic."""
    retriever = ResearchRetriever()
    chunks = retriever.retrieve(query=topic, top_k=top_k)
    logger.info("Tool: retrieved %d chunks for topic '%s'", len(chunks), topic)
    return {
        "status": "completed",
        "topic": topic,
        "chunks_retrieved": len(chunks),
        "results": chunks,
    }



