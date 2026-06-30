import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_api_base: str | None = os.getenv("LLM_API_BASE")
    llm_api_key: str | None = os.getenv("LLM_API_KEY")
    llm_model_name: str | None = os.getenv("LLM_MODEL_NAME")


settings = Settings()
