from __future__ import annotations

from typing import Any

from app.tools.langgraph_workflow import get_graph
from app.tools.langgraph_workflow.state import ScriptState
from core.logs import logger


class ScriptQuestionTool:
    """
    3-tool interface backed by a LangGraph workflow in app/tools/langgraph_workflow/.

    tool.start(topic, existing_script)   → structure + first questions
    tool.answer_and_finalize(answers)    → more questions OR final_script
    """

    def __init__(self) -> None:
        self._state: ScriptState | None = None

    # ------------------------------------------------------------------
    # Tool 2 of 3
    # ------------------------------------------------------------------

    def start(self, topic: str, existing_script: str = "") -> dict[str, Any]:
        if not topic or not topic.strip():
            raise ValueError("topic must not be empty")

        initial_state: ScriptState = {
            "topic": topic.strip(),
            "existing_script": existing_script,
            "structure": None,
            "analysis": None,
            "qa_pairs": [],
            "pending_questions": [],
            "remaining_gaps": [],
            "batch_counter": 0,
            "total_tokens": 0,
            "final_script": None,
            "current_answers": {},
            "needs_more_questions": True,
        }

        logger.info("ScriptQuestionTool.start: topic='%s'", topic)
        # Runs analyze_topic → generate_questions → END
        result = get_graph().invoke(initial_state)
        self._state = result

        return {
            "structure": result["structure"],
            "analysis": result["analysis"],
            "questions": result["pending_questions"],
            "batch_number": result["batch_counter"],
            "total_tokens": result["total_tokens"],
        }

    # ------------------------------------------------------------------
    # Tool 3 of 3  (answer + finalize merged)
    # ------------------------------------------------------------------

    def answer_and_finalize(self, answers: dict[str, str]) -> dict[str, Any]:
        if self._state is None:
            raise RuntimeError("Call start() before answer_and_finalize()")

        logger.info("ScriptQuestionTool.answer_and_finalize")
        # process_answers → conditional → (generate_questions | write_script) → END
        result = get_graph().invoke({**self._state, "current_answers": answers})
        self._state = result

        if result["final_script"] is not None:
            return {
                "needs_more": False,
                "final_script": result["final_script"],
                "total_tokens": result["total_tokens"],
            }

        return {
            "needs_more": True,
            "questions": result["pending_questions"],
            "remaining_gaps": result["remaining_gaps"],
            "total_tokens": result["total_tokens"],
        }
