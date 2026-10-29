import re
from pathlib import Path
from typing import Any

from app.tools.script_tool.schemas import ScriptStructure
from core.logs import logger


OUTPUT_DIR = Path("data/scripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


SCRIPT_STORE_TOOL_SCHEMA: dict[str, Any] = {
    "name": "store_script",
    "description": (
        "Save the script written so far to a .txt file and check it against the structure. "
        "Returns the full script text and completed=true only when every section of the "
        "structure is present and meets the minimum word count of its word_count_range."
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
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of a section in the structure."},
                        "content": {"type": "string", "description": "Spoken text of the section."},
                    },
                    "required": ["name", "content"],
                },
                "description": "The sections written so far.",
            },
        },
        "required": ["topic", "structure", "sections"],
    },
}


def _min_words(word_count_range: str) -> int:
    """Lower bound of a range like '120-150'; 1 if it cannot be parsed."""
    numbers = re.findall(r"\d+", word_count_range)
    return int(numbers[0]) if numbers else 1


def store_script(
    topic: str, structure: dict[str, Any], sections: list[dict[str, str]]
) -> dict[str, Any]:
    """Write the script to a txt file and report whether every section is fully covered."""
    if not topic or not topic.strip():
        raise ValueError("topic must not be empty")
    topic = topic.strip()

    script_structure = ScriptStructure.model_validate(structure)
    written = {s["name"]: s["content"].strip() for s in sections}

    parts: list[str] = []
    missing: list[str] = []
    incomplete: list[str] = []
    for section in script_structure.sections:
        content = written.get(section.name, "")
        if not content:
            missing.append(section.name)
            continue
        parts.append(f"## {section.name}\n\n{content}")
        if len(content.split()) < _min_words(section.word_count_range):
            incomplete.append(section.name)

    script = f"# {topic}\n\n" + "\n\n".join(parts)
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")[:60] or "script"
    path = OUTPUT_DIR / f"{slug}.txt"
    path.write_text(script, encoding="utf-8")

    completed = not missing and not incomplete
    logger.info("Tool: stored script for '%s' at %s (completed=%s)", topic, path, completed)
    return {
        "status": "completed",
        "topic": topic,
        "completed": completed,
        "missing_sections": missing,
        "incomplete_sections": incomplete,
        "file_path": str(path),
        "script": script,
        "total_words": len(script.split()),
    }
