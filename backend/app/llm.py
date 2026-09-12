import os
from functools import lru_cache

from langchain_openrouter import ChatOpenRouter

from app.config import OPENROUTER_MODEL
from app.schemas import IntentData


@lru_cache
def get_structured_llm():
    if not os.getenv("OPENROUTER_API_KEY"):
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your OpenRouter API key."
        )
    model = ChatOpenRouter(model=OPENROUTER_MODEL, temperature=0)
    return model.with_structured_output(IntentData)
