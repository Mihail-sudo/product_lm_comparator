import json
import re
from typing import Optional, Dict, Any

import httpx
from bs4 import BeautifulSoup

from .llm_client import call_ollama, DEFAULT_MODEL


def fetch_page_text(url: str) -> Optional[str]:
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; SupplierParser/1.0; "
                        "+https://github.com/product_lm_comparator)"
                    )
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)[:15000]
    except Exception as e:
        print(f"Error fetching URL {url}: {e}", flush=True)
        return None


EXTRACTION_SYSTEM_PROMPT = """Ты — ассистент по извлечению данных о компаниях-поставщиках.

Извлеки из текста сайта информацию о компании и верни ТОЛЬКО JSON без лишнего текста.
Формат JSON:
{
  "name": "Название компании",
  "description": "Описание деятельности",
  "address": "Полный адрес",
  "locations": [{"city": "Город", "region": "Регион"}],
  "foundation_year": 2000,
  "categories": ["Категория1", "Категория2"],
  "contacts": [
    {"type": "phone/email/telegram/whatsapp/viber", "value": "+7-...", "contact_person": null, "is_primary": false}
  ],
  "certificates": [
    {"certificate_name": "Название сертификата", "certificate_type": "iso/quality/safety/organic/halal/kosher", "issuing_authority": "Кто выдал", "is_valid": true}
  ],
  "order_conditions": [
    {"category_name": "Категория", "min_order_quantity": 100, "min_order_unit": "kg/ton/piece/box/pallet/liter", "price_per_unit": 100.50, "price_currency": "RUB", "price_negotiable": true, "delivery_terms": "Условия доставки", "delivery_region": "Регион доставки", "delivery_cost": 500, "payment_terms": "Условия оплаты", "lead_time_days": 3}
  ]
}

ВАЖНО: В поле categories указывай ТОЛЬКО категории, которые явно и недвусмысленно описаны в тексте сайта. Каждая категория должна быть напрямую подтверждена содержимым сайта. Не выдумывай категории и не делай предположений — если на сайте нет прямого упоминания деятельности в определённой категории, не включай её.
Если данных нет — используй null или []. Не добавляй ничего до или после JSON."""


def parse_supplier_from_url(
    url: str, model: str = DEFAULT_MODEL,
    existing_categories: Optional[list[str]] = None,
) -> Optional[Dict[str, Any]]:
    page_text = fetch_page_text(url)
    if not page_text:
        return None

    cat_hint = ""
    if existing_categories:
        cat_hint = (
            "\n\nВ системе есть такие категории: "
            + ", ".join(existing_categories)
            + ".\nВыбери из них наиболее подходящие, строго основываясь на тексте сайта. "
            "Категорически запрещено придумывать категории, которых нет в этом списке. "
            "Включай только те категории, которые явно подтверждены текстом сайта."
        )

    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Извлеки данные о компании-поставщике:{cat_hint}\n\n{page_text}",
        },
    ]

    result = call_ollama(messages, model)
    if not result:
        return None

    json_match = re.search(r"\{.*\}", result, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            data.setdefault("website", url)
            return data
        except json.JSONDecodeError:
            return None

    try:
        data = json.loads(result)
        data.setdefault("website", url)
        return data
    except json.JSONDecodeError:
        return None
