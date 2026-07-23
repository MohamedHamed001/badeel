"""Provider factory (spec section 4).

Selected purely by environment variables — no code changes to switch between a
local Ollama daemon and any OpenAI-compatible endpoint (Ollama Cloud,
OpenRouter, LM Studio, Together, vLLM).
"""

import os

from langchain_core.language_models import BaseChatModel


def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    LLM_PROVIDER=ollama          local Ollama daemon
    LLM_PROVIDER=openai_compat   anything speaking the OpenAI API
    """
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model,
            base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            temperature=temperature,
            num_ctx=8192,
        )

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model,
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY", "not-needed"),
        temperature=temperature,
        timeout=60,
        max_retries=2,
    )


def llm_available() -> bool:
    """Cheap reachability probe. Used to decide whether to narrate or degrade
    to the deterministic pipeline (spec section 13)."""
    try:
        get_llm().invoke("ok")
        return True
    except Exception:
        return False
