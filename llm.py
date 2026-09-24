from functools import lru_cache

from langchain.chat_models import init_chat_model

from config import (
    LM_STUDIO_BASE_URL,
    LOCAL_LLM_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL
)


@lru_cache(maxsize=2)
def get_llm(mode: str):

    if mode == "offline":

        return init_chat_model(
            model=LOCAL_LLM_MODEL,
            model_provider="openai",
            base_url=LM_STUDIO_BASE_URL,
            api_key="dummy",
            temperature=0.2
        )

    if mode == "online":

        if not GEMINI_API_KEY:
            raise ValueError(
                "Gemini API key is missing."
            )

        return init_chat_model(
            model=GEMINI_MODEL,
            model_provider="google_genai",
            api_key=GEMINI_API_KEY
        )

    raise ValueError(
        f"Unsupported mode: {mode}"
    )