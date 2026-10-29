from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from langchain_core.tools import tool
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.prebuilt import ToolNode, create_react_agent

from app.tools.answer_tool import ANSWER_TOOL_SCHEMA, answer_question
from app.tools.prompts.agent_prompt import AGENT_SYSTEM_PROMPT, format_tool_reference
from app.tools.question_tool import QUESTION_TOOL_SCHEMA, ask_questions
from app.tools.retriever_tool import RETRIEVER_TOOL_SCHEMA, retrieve_context
from app.tools.script_store_tool import SCRIPT_STORE_TOOL_SCHEMA, store_script
from app.tools.section_tool import SECTION_TOOL_SCHEMA, write_section
from app.tools.structure_tool import STRUCTURE_TOOL_SCHEMA, create_structure
from app.tools.validation_tool import VALIDATION_TOOL_SCHEMA, validate_qa
from core.config import settings
from core.logs import logger


MAX_NUDGES = 8


def _tool(schema: dict[str, Any]):
    """@tool whose name, description and argument schema come from the tool's own *_TOOL_SCHEMA."""
    return tool(schema["name"], description=schema["description"], args_schema=schema["input_schema"])


def _tool_error(exc: Exception) -> str:
    """Hand tool failures back to the agent as a message so it can retry instead of aborting the run."""
    logger.warning("Tool error: %s", exc)
    return f"Tool failed: {exc}. Fix the arguments or retry the call."


@_tool(RETRIEVER_TOOL_SCHEMA)
def retrieval_agent(**kwargs: Any) -> dict[str, Any]:
    return retrieve_context(**kwargs)


@_tool(QUESTION_TOOL_SCHEMA)
def question_agent(**kwargs: Any) -> dict[str, Any]:
    return ask_questions(**kwargs)


@_tool(STRUCTURE_TOOL_SCHEMA)
def structure_agent(**kwargs: Any) -> dict[str, Any]:
    return create_structure(**kwargs)


@_tool(ANSWER_TOOL_SCHEMA)
def answer_agent(**kwargs: Any) -> dict[str, Any]:
    return answer_question(**kwargs)


@_tool(VALIDATION_TOOL_SCHEMA)
def validation_agent(**kwargs: Any) -> dict[str, Any]:
    return validate_qa(**kwargs)


@_tool(SECTION_TOOL_SCHEMA)
def section_agent(**kwargs: Any) -> dict[str, Any]:
    return write_section(**kwargs)


@_tool(SCRIPT_STORE_TOOL_SCHEMA)
def script_store_agent(**kwargs: Any) -> dict[str, Any]:
    return store_script(**kwargs)


TOOLS = [
    structure_agent,
    question_agent,
    retrieval_agent,
    answer_agent,
    validation_agent,
    section_agent,
    script_store_agent,
]

TOOL_SCHEMAS = [
    STRUCTURE_TOOL_SCHEMA,
    QUESTION_TOOL_SCHEMA,
    RETRIEVER_TOOL_SCHEMA,
    ANSWER_TOOL_SCHEMA,
    VALIDATION_TOOL_SCHEMA,
    SECTION_TOOL_SCHEMA,
    SCRIPT_STORE_TOOL_SCHEMA,
]

# The shared llm in app.llm forces JSON output, which breaks tool calling, so the agent gets its own.
agent_llm = ChatNVIDIA(
    model=settings.model_name,
    temperature=0.3,
    max_tokens=4096,
    timeout=240,
    api_key=settings.nvidia_api_key,
    model_kwargs={"chat_template_kwargs": {"enable_thinking": False}},
)


@lru_cache(maxsize=1)
def get_agent():
    """Return the singleton LangGraph agent: an LLM that decides which tool to call next."""
    return create_react_agent(agent_llm, ToolNode(TOOLS, handle_tool_errors=_tool_error), prompt=AGENT_SYSTEM_PROMPT + format_tool_reference(TOOL_SCHEMAS))


def generate_script(topic: str, existing_script: str = "") -> dict[str, Any]:
    """Run the agent for a topic; returns its final message and the stored script (if any)."""
    request = f"Topic: {topic}\n\nExisting script:\n{existing_script or '(none)'}"
    logger.info("Agent: starting for '%s'", topic)
    messages: list[Any] = [("user", request)]
    stored = None
    for attempt in range(MAX_NUDGES + 1):
        state = get_agent().invoke({"messages": messages}, config={"recursion_limit": 100})
        messages = state["messages"]
        stored = _find_stored(messages)
        if stored and stored.get("completed"):
            break
        # The model sometimes ends its turn (often with an empty reply) before the script is stored.
        logger.warning("Agent stopped before the script was completed (attempt %d); nudging", attempt + 1)
        messages = messages + [(
            "user",
            "You are not finished: the script has not been stored with completed=true. "
            "Continue with the next tool call (validate_qa, write_section, store_script) until it is.",
        )]

    return {"summary": messages[-1].content if hasattr(messages[-1], "content") else "", "stored": stored}


def _find_stored(messages: list[Any]) -> dict[str, Any] | None:
    """Latest parsed store_script result in the message history, if any."""
    stored = None
    for msg in messages:
        if getattr(msg, "name", None) == "store_script":
            try:
                stored = json.loads(msg.content)
            except (TypeError, ValueError):
                pass
    return stored
