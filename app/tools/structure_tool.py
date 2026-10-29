from typing import Any

from app.llm import llm_call
from app.tools.prompts.structure_prompt import STRUCTURE_PROMPT
from app.tools.script_tool.schemas import ScriptStructure
from core.logs import logger


STRUCTURE_TOOL_SCHEMA: dict[str, Any] = {
    "name": "create_structure",
    "description": (
        "Create the ideal structure for an 8-minute educational video script. "
        "Returns the ordered sections, each with its name, duration, word-count "
        "range, purpose and the key points it must cover."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic of the video script.",
            },
        },
        "required": ["topic"],
    },
}


def create_structure(topic: str) -> dict[str, Any]:
    """Build a section-by-section script structure for the given topic."""
    if not topic or not topic.strip():
        raise ValueError("topic must not be empty")
    topic = topic.strip()

    r = llm_call(ScriptStructure, STRUCTURE_PROMPT, {"topic": topic})
    structure: ScriptStructure = r["response"]

    section_names = [section.name for section in structure.sections]
    logger.info(
        "Tool: created %d-section structure for topic '%s': %s",
        len(section_names),
        topic,
        ", ".join(section_names),
    )
    return {
        "status": "completed",
        "topic": topic,
        "structure": structure.model_dump(),
        "total_tokens": r["token_used"],
    }
