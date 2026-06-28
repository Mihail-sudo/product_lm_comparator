import requests
import os
import sys
import json
from typing import List, Dict, Optional, Tuple

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")


def _format_suppliers_context(suppliers: List[Dict]) -> str:
    parts = []
    for i, s in enumerate(suppliers, 1):
        part = f"{i}. {s.get('name', 'N/A')} (г. {s.get('city', 'N/A')})"
        desc = s.get("description", "")
        if desc:
            part += f"\n   Описание: {desc[:300]}"
        contacts = s.get("contact", [])
        if contacts:
            c_str = "; ".join(
                f"{c.get('contact_person', '')}: {c.get('contact_value', '')}"
                for c in contacts[:3]
            )
            part += f"\n   Контакты: {c_str}"
        certs = s.get("certificates", [])
        if certs:
            cert_str = ", ".join(c.get("certificate_name", "") for c in certs[:5])
            part += f"\n   Сертификаты: {cert_str}"
        notes = s.get("notes", [])
        if notes:
            note_str = "; ".join(n.get("text", "")[:100] for n in notes[:3])
            part += f"\n   Заметки: {note_str}"
        parts.append(part)
    return "\n\n".join(parts)


def _debug(msg: str):
    print(msg, file=sys.stderr, flush=True)


def _probe(method: str, path: str, **kwargs) -> str:
    try:
        resp = requests.request(method, f"{OLLAMA_BASE_URL}{path}", timeout=5, **kwargs)
        parts = [f"{method} {path} — status={resp.status_code}"]
        ct = resp.headers.get("Content-Type", "")
        parts.append(f"Content-Type: {ct}")
        if len(resp.content) < 500:
            parts.append(f"body={resp.text[:300]}")
        else:
            parts.append(f"body={resp.text[:100]}...")
        return " | ".join(parts)
    except Exception as e:
        return f"{method} {path} — {type(e).__name__}: {e}"


LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))


def _post_json(path: str, body: dict) -> Tuple[Optional[dict], Optional[str]]:
    raw = json.dumps(body)
    _debug(f"sending to {path}: {raw[:200]}")
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}{path}",
            data=raw,
            headers={"Content-Type": "application/json"},
            timeout=LLM_TIMEOUT,
        )
        info = f"POST {path} — status={resp.status_code}, body={resp.text[:200]}"
        if resp.status_code == 404:
            return None, info
        resp.raise_for_status()
        return resp.json(), info
    except requests.exceptions.ConnectionError as e:
        return None, f"POST {path} — ConnectionError: {e}"
    except Exception as e:
        return None, f"POST {path} — {type(e).__name__}: {e}"


def _call_ollama(messages: List[Dict], model: str = DEFAULT_MODEL) -> Optional[str]:
    _debug(f"OLLAMA_BASE_URL={OLLAMA_BASE_URL}")
    _debug(f"model={model}")

    _debug(_probe("GET", "/"))
    _debug(_probe("GET", "/api/version"))
    _debug(_probe("GET", "/api/tags"))

    body = {"model": model, "prompt": _to_flat_prompt(messages), "stream": False}
    data, info = _post_json("/api/generate", body)
    _debug(info)
    if data:
        return data.get("response", "")

    body = {"model": model, "messages": messages, "stream": False}
    data, info = _post_json("/api/chat", body)
    _debug(info)
    if data:
        return data.get("message", {}).get("content", "")

    return None


def _to_flat_prompt(messages: List[Dict]) -> str:
    lines = []
    for msg in messages:
        role = msg["role"].capitalize()
        lines.append(f"{role}: {msg['content']}")
    lines.append("Assistant: ")
    return "\n\n".join(lines)


def generate_recommendation_llm(
    suppliers: List[Dict], model: str = DEFAULT_MODEL
) -> Optional[str]:
    context = _format_suppliers_context(suppliers)
    messages = [
        {
            "role": "system",
            "content": (
                "Ты — эксперт по анализу поставщиков продуктов питания. "
                "Проанализируй предоставленных поставщиков и дай рекомендацию. "
                "Ответ напиши на русском языке. Выдели сильные и слабые стороны каждого. "
                "В конце дай четкую рекомендацию, кого выбрать и почему."
            ),
        },
        {
            "role": "user",
            "content": f"Вот данные о поставщиках:\n\n{context}\n\nДайте рекомендацию.",
        },
    ]
    return _call_ollama(messages, model)


def ask_bot_llm(
    question: str, suppliers: List[Dict], model: str = DEFAULT_MODEL
) -> Optional[str]:
    context = _format_suppliers_context(suppliers)
    messages = [
        {
            "role": "system",
            "content": (
                "Ты — бот-помощник для сравнения поставщиков продуктов питания. "
                "Отвечай на вопросы пользователя, используя только предоставленные данные. "
                "Ответы пиши на русском языке, будь краток и по делу. "
                "Если данных для ответа недостаточно, честно скажи об этом."
            ),
        },
        {
            "role": "user",
            "content": f"Данные о поставщиках:\n\n{context}\n\nВопрос: {question}",
        },
    ]
    return _call_ollama(messages, model)
