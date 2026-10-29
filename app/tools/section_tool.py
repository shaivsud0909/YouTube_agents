from typing import Any

from app.llm import llm_call
from app.tools.prompts.section_prompt import SECTION_SCRIPT_PROMPT
from app.tools.script_tool.schemas import ScriptSection, SectionDraft
from core.logs import logger


SECTION_TOOL_SCHEMA: dict[str, Any] = {
    "name": "write_section",
    "description": (
        "Write the spoken text of one script section, using the validated question/answer "
        "pairs as source material and the previous section for continuity."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "The topic of the video script."},
            "section": {
                "type": "object",
                "description": "One entry of the `sections` list from the create_structure tool.",
            },
            "section_index": {"type": "integer", "description": "1-based position of the section."},
            "section_count": {"type": "integer", "description": "Total number of sections."},
            "qa_pairs": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Validated {question, answer} pairs.",
            },
            "previous_text": {"type": "string", "description": "Text of the previous section.", "default": ""},
            "existing_script": {"type": "string", "description": "Existing draft, if any.", "default": ""},
        },
        "required": ["topic", "section", "section_index", "section_count", "qa_pairs"],
    },
}


def write_section(
    topic: str,
    section: dict[str, Any],
    section_index: int,
    section_count: int,
    qa_pairs: list[dict[str, str]],
    previous_text: str = "",
    existing_script: str = "",
) -> dict[str, Any]:
    """Write the spoken text for one section."""
    sec = ScriptSection.model_validate(section)
    all_qa = (
        "\n".join(f"Q: {p['question']}\nA: {p['answer']}" for p in qa_pairs)
        if qa_pairs
        else "None."
    )

    r = llm_call(
        SectionDraft,
        SECTION_SCRIPT_PROMPT,
        {
            "topic": topic,
            "section_json": sec.model_dump_json(indent=2),
            "section_index": section_index,
            "section_count": section_count,
            "previous_text": previous_text,
            "existing_script": existing_script or "(none)",
            "all_qa": all_qa,
        },
    )
    content = r["response"].content.strip()

    logger.info("Tool: wrote section %d/%d '%s'", section_index, section_count, sec.name)
    return {
        "status": "completed",
        "name": sec.name,
        "content": content,
        "word_count": len(content.split()),
        "total_tokens": r["token_used"],
    }
