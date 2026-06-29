import requests
import os
import datetime
from requests.exceptions import ConnectionError, Timeout
from .exceptions import ApiError


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "suppliers/"


def from_iso(date_time):
    date_time = datetime.datetime.fromisoformat(date_time)
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def _get_json(path, params=None):
    try:
        resp = requests.get(BASE_URL + path, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except ConnectionError:
        raise ApiError("Не удалось подключиться к серверу. Запущен ли бекенд (порт 8000)?")
    except Timeout:
        raise ApiError("Сервер не ответил вовремя. Попробуйте позже.")
    except requests.exceptions.HTTPError as e:
        raise ApiError(f"Сервер вернул ошибку: {e}")


def get_suppliers_by_filter(**params):
    data = _get_json("search", params=params)
    category_id = params.get("category_id")
    return [
        {
            "name": supplier.get("name"),
            "city": supplier.get("city"),
            "locations": supplier.get("locations", []),
            "address": supplier.get("address"),
            "id": supplier.get("id"),
            "description": supplier.get("description"),
            "notes": [
                {
                    "text": note.get("note_text"),
                    "note_type": note.get("note_type"),
                    "date": from_iso(note.get("created_at"))
                }
                for note in (supplier.get("notes") or [])
            ],
            "contact": [
                {
                    'contact_person': contact.get('contact_person'),
                    'contact_type': contact.get('contact_type'),
                    'contact_value': contact.get('contact_value')
                }
                for contact in (supplier.get("contacts") or [])
                if contact.get("is_primary", False)
            ],
            "category": [
                (category.get("id"), category.get("name"))
                for category in (supplier.get("categories") or [])
                if category.get("id") == category_id
            ],
            "certificates": [
                {
                    "certificate_name": certificate.get("certificate_name"),
                    "issuing_authority": certificate.get("issuing_authority")
                }
                for certificate in (supplier.get("certificates") or [])
            ]
        } for supplier in data["items"]
    ]


def get_supplier_cities():
    data = _get_json("", params={"limit": 100})
    cities = set()
    for s in data["items"]:
        for loc in s.get("locations") or []:
            if loc.get("city"):
                cities.add(loc["city"])
    return sorted(cities)


def get_supplier_regions():
    data = _get_json("", params={"limit": 100})
    regions = set()
    for s in data["items"]:
        for loc in s.get("locations") or []:
            if loc.get("region"):
                regions.add(loc["region"])
    return sorted(regions)


if __name__ == "__main__":
    result = get_supplier_regions()
    print(result)
