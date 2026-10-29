from typing import Any

from app.llm import llm_call
from app.tools.answer_tool import _format_chunks
from app.tools.prompts.validation_prompt import VALIDATION_PROMPT
from app.tools.script_tool.schemas import QAValidation
from core.logs import logger


VALIDATION_TOOL_SCHEMA: dict[str, Any] = {
    "name": "validate_qa",
    "description": (
        "Validate a generated question and its answer. Checks that the question is relevant "
        "and clear, that the answer addresses it, and that every claim in the answer is "
        "supported by the retrieved chunks. Returns is_valid plus the list of issues."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic of the video script.",
            },
            "question": {
                "type": "string",
                "description": "The generated question.",
            },
            "answer": {
                "type": "string",
                "description": "The answer returned by the answer_question tool.",
            },
            "results": {
                "type": "array",
                "items": {"type": "object"},
                "description": "The `results` list returned by the retrieve_context tool.",
            },
        },
        "required": ["topic", "question", "answer", "results"],
    },
}


def validate_qa(
    topic: str, question: str, answer: str, results: list[dict[str, Any]]
) -> dict[str, Any]:
    """Validate the question/answer pair against the topic and retrieved chunks."""
    if not question or not question.strip():
        raise ValueError("question must not be empty")
    if not answer or not answer.strip():
        raise ValueError("answer must not be empty")

    r = llm_call(
        QAValidation,
        VALIDATION_PROMPT,
        {
            "topic": topic,
            "question": question.strip(),
            "answer": answer.strip(),
            "retrieved_context": _format_chunks(results),
        },
    )
    v: QAValidation = r["response"]

    logger.info("Tool: validated question '%s' (is_valid=%s)", question, v.is_valid)
    return {
        "status": "completed",
        "question": question,
        "is_valid": v.is_valid,
        "validation": v.model_dump(),
        "total_tokens": r["token_used"],
    }
