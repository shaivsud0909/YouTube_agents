from typing import Any

from app.llm import llm_call
from app.tools.prompts.analysis_prompt import ANALYSIS_PROMPT
from app.tools.prompts.questions_prompt import QUESTIONS_PROMPT
from app.tools.script_tool.schemas import QuestionBatch, ScriptAnalysis, ScriptStructure
from core.logs import logger


QUESTION_TOOL_SCHEMA: dict[str, Any] = {
    "name": "ask_questions",
    "description": (
        "Compare an existing script draft against the ideal script structure, find the gaps, "
        "and return a prioritised batch of questions to fill them. "
        "Also returns the gap analysis."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic of the video script.",
            },
            "structure": {
                "type": "object",
                "description": "The script structure, as returned by the create_structure tool.",
            },
            "existing_script": {
                "type": "string",
                "description": "The script written so far (may be empty).",
                "default": "",
            },
        },
        "required": ["topic", "structure"],
    },
}


def ask_questions(topic: str, structure: dict[str, Any], existing_script: str = "") -> dict[str, Any]:
    """Generate gap-filling questions for the given topic and existing script."""
    if not topic or not topic.strip():
        raise ValueError("topic must not be empty")
    topic = topic.strip()

    script_structure = ScriptStructure.model_validate(structure)

    r1 = llm_call(
        ScriptAnalysis,
        ANALYSIS_PROMPT,
        {
            "topic": topic,
            "structure_json": script_structure.model_dump_json(indent=2),
            "existing_script": existing_script or "(none)",
        },
    )
    analysis: ScriptAnalysis = r1["response"]

    r2 = llm_call(
        QuestionBatch,
        QUESTIONS_PROMPT,
        {
            "topic": topic,
            "analysis_json": analysis.model_dump_json(indent=2),
            "answered_so_far": "None yet.",
        },
    )
    batch: QuestionBatch = r2["response"]

    logger.info("Tool: generated %d questions for topic '%s'", len(batch.questions), topic)
    return {
        "status": "completed",
        "topic": topic,
        "analysis": analysis.model_dump(),
        "questions": [q.model_dump() for q in batch.questions],
        "total_tokens": r1["token_used"] + r2["token_used"],
    }
