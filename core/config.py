from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]



class Settings(BaseSettings):
    # Application
    title: str = "Boiler"
    description: str = "Boilerplate FastAPI project"
    version: str = "1.0.0"
    debug: bool = False

    port: int = 8000

    # Environment configuration
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    youtube_api_key: str

    # NVIDIA
    model_name: str = "openai/gpt-oss-20b"
    nvidia_api_key: str


settings = Settings()