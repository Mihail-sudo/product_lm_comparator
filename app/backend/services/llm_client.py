import os
import json
from typing import Optional, List, Dict

import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))


def _to_flat_prompt(messages: List[Dict]) -> str:
    lines = []
    for msg in messages:
        role = msg["role"].capitalize()
        lines.append(f"{role}: {msg['content']}")
    lines.append("Assistant: ")
    return "\n\n".join(lines)


def call_ollama(messages: List[Dict], model: str = DEFAULT_MODEL) -> Optional[str]:
    try:
        with httpx.Client(timeout=LLM_TIMEOUT) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
    except Exception:
        pass

    try:
        with httpx.Client(timeout=LLM_TIMEOUT) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": _to_flat_prompt(messages), "stream": False},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
    except Exception:
        pass

    return None
