import json
from typing import Any

from core.logs import logger
from app.rag.retriver import ResearchRetriever


RETRIEVER_TOOL_SCHEMA: dict[str, Any] = {
    "name": "retrieve_context",
    "description": (
        "Search the vector database for chunks relevant to a question. "
        "Returns the top matching text chunks with their metadata and similarity scores. "
        "Call this before answering a question to ground your response in stored research."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question to search for in the vector database.",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of chunks to retrieve (1–20, default: 5).",
                "default": 5,
            },
        },
        "required": ["question"],
    },
}


def retrieve_context(question: str, top_k: int = 5) -> dict[str, Any]:
    """Retrieve relevant chunks from the vector DB for the given question."""
    retriever = ResearchRetriever()
    chunks = retriever.retrieve(query=question, top_k=top_k)
    logger.info("Tool: retrieved %d chunks for question '%s'", len(chunks), question)
    return {
        "status": "completed",
        "question": question,
        "chunks_retrieved": len(chunks),
        "results": chunks,
    }



