import os
import json
import sys
from typing import List, Dict, Optional

import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))


def to_flat_prompt(messages: List[Dict]) -> str:
    lines = []
    for msg in messages:
        role = msg["role"].capitalize()
        lines.append(f"{role}: {msg['content']}")
    lines.append("Assistant: ")
    return "\n\n".join(lines)


def call_ollama(
    messages: List[Dict],
    model: str = DEFAULT_MODEL,
    prefer_generate: bool = False,
    debug: bool = False,
) -> Optional[str]:
    if debug:
        print(f"OLLAMA_BASE_URL={OLLAMA_BASE_URL}", file=sys.stderr)
        print(f"model={model}", file=sys.stderr)

    endpoints = ["/api/generate", "/api/chat"] if prefer_generate else ["/api/chat", "/api/generate"]

    for endpoint in endpoints:
        try:
            if endpoint == "/api/generate":
                body = {"model": model, "prompt": to_flat_prompt(messages), "stream": False}
            else:
                body = {"model": model, "messages": messages, "stream": False}

            resp = requests.post(
                f"{OLLAMA_BASE_URL}{endpoint}",
                json=body,
                timeout=LLM_TIMEOUT,
            )
            if debug:
                print(f"POST {endpoint} — status={resp.status_code}", file=sys.stderr)

            if resp.status_code == 200:
                data = resp.json()
                if endpoint == "/api/generate":
                    return data.get("response", "")
                return data.get("message", {}).get("content", "")

            if debug:
                print(f"  body={resp.text[:200]}", file=sys.stderr)

        except requests.exceptions.ConnectionError as e:
            if debug:
                print(f"ConnectionError: {e}", file=sys.stderr)
        except Exception as e:
            if debug:
                print(f"{type(e).__name__}: {e}", file=sys.stderr)

    return None
