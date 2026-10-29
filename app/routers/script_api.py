from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import app.tools.script_tool  # noqa: F401  (must load before langgraph_workflow: circular import)
from app.tools.langgraph_workflow.graph import get_graph
from core.logs import logger

script_router = APIRouter()


class GenerateInput(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    existing_script: str = ""


def _initial_state(topic: str, existing_script: str) -> dict:
    return {
        "topic": topic,
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
        "needs_more_questions": False,
    }


@script_router.post("/generate")
def generate_script(body: GenerateInput):
    """Run the full workflow: analyse, self-answer via retrieval, write the script."""
    try:
        result = get_graph().invoke(_initial_state(body.topic, body.existing_script))
    except Exception as exc:
        logger.exception("Script workflow failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "final_script": result["final_script"],
        "qa_pairs": result["qa_pairs"],
        "batches": result["batch_counter"],
        "total_tokens": result["total_tokens"],
    }
