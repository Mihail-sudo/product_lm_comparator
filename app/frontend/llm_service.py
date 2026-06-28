import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import List, Dict, Optional
from app.frontend.llm_common import call_ollama, DEFAULT_MODEL


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
    return call_ollama(messages, model, prefer_generate=False, debug=False)


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
    return call_ollama(messages, model, prefer_generate=False, debug=False)
