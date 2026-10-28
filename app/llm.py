from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from core.config import settings
from core.logs import logger


def _load_credentials():
    if not settings.google_credentials_path:
        return None
    try:
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            settings.google_credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
    except Exception as exc:
        logger.warning("Could not load Google credentials from path: %s", exc)
        return None


llm = ChatGoogleGenerativeAI(
    model=settings.model_name,
    project=settings.google_project or None,
    credentials=_load_credentials(),
    location=settings.google_location,
    vertexai=bool(settings.google_project),
    thinking_level="minimal",
)


def llm_call(py_class, prompt: PromptTemplate, inputs: dict) -> dict:
    """Invoke a structured-output chain and return parsed response + token count."""
    try:
        chain = prompt | llm.with_structured_output(py_class, include_raw=True)
        response = chain.invoke(inputs)
        usage = response["raw"].usage_metadata
        tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        return {"response": response["parsed"], "token_used": tokens_used}
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc
