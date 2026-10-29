from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents import generate_script
from core.logs import logger

agent_router = APIRouter()


class GenerateInput(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    existing_script: str = ""


@agent_router.post("/generate")
def generate(body: GenerateInput):
    """Run the scriptwriting agent for a topic."""
    try:
        return generate_script(body.topic, body.existing_script)
    except Exception as exc:
        logger.exception("Agent run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
