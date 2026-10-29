from typing import Any

from app.llm import llm_call
from app.tools.prompts.answer_prompt import ANSWER_PROMPT
from app.tools.script_tool.schemas import GroundedAnswer
from core.logs import logger


ANSWER_TOOL_SCHEMA: dict[str, Any] = {
    "name": "answer_question",
    "description": (
        "Answer a question using only the chunks returned by the retrieve_context tool. "
        "If the chunks do not cover the question, says so instead of inventing facts."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question to answer.",
            },
            "results": {
                "type": "array",
                "items": {"type": "object"},
                "description": "The `results` list returned by the retrieve_context tool.",
            },
        },
        "required": ["question", "results"],
    },
}


def _format_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context found in the research database."
    return "\n\n".join(f"[{i + 1}] {c['text']}" for i, c in enumerate(chunks))


def answer_question(question: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    """Answer the question from the retrieved chunks."""
    if not question or not question.strip():
        raise ValueError("question must not be empty")
    question = question.strip()

    r = llm_call(
        GroundedAnswer,
        ANSWER_PROMPT,
        {"question": question, "retrieved_context": _format_chunks(results)},
    )
    result: GroundedAnswer = r["response"]

    logger.info("Tool: answered question '%s' (answered=%s)", question, result.answered)
    return {
        "status": "completed",
        "question": question,
        "answer": result.answer,
        "answered": result.answered,
        "total_tokens": r["token_used"],
    }
