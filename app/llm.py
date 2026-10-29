from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from core.config import settings


llm = ChatNVIDIA(
    model=settings.model_name,
    temperature=1,
    max_tokens=2048,
    api_key=settings.nvidia_api_key,
    model_kwargs={
        "response_format": {"type": "json_object"},
        "chat_template_kwargs": {"enable_thinking": False},
    },
)


def llm_call(py_class, prompt: PromptTemplate, inputs: dict) -> dict:
    """Invoke a structured-output chain and return parsed response + token count."""
    try:
        # ChatNVIDIA doesn't support include_raw, so parse the JSON output ourselves.
        parser = PydanticOutputParser(pydantic_object=py_class)
        text = prompt.format(**inputs) + "\n\n" + parser.get_format_instructions()
        raw = llm.invoke(text)
        usage = raw.usage_metadata or {}
        tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        return {"response": parser.parse(raw.content), "token_used": tokens_used}
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc
