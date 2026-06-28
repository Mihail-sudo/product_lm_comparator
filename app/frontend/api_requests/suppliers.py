import requests
import os
import asyncio
import datetime


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "suppliers/"


def from_iso(date_time):
    date_time = datetime.datetime.fromisoformat(date_time)
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


async def get_suppliers_by_filter(**params):
    try: 
        suppliers = requests.get(BASE_URL + "search", params=params).json()
        category_id = params["category_id"]
        # result = suppliers
        result = [
            {
                "name": supplier.get("name"),
                "city": supplier.get("city"),
                "address": supplier.get("address"),
                "id": supplier.get("id"),
                "description": supplier.get("description"),
                "notes": [
                    {
                        "text": note.get("note_text"),
                        "note_type": note.get("note_type"),
                        "date": from_iso(note.get("created_at"))
                    }
                    for note in supplier.get("notes", [{}])
                ],
                "contact": [ 
                    {
                        'contact_person': contact.get('contact_person'),
                        'contact_type': contact.get('contact_type'),
                        'contact_value': contact.get('contact_value')
                    }
                    for contact in supplier.get("contacts")
                    if contact.get("is_primary", False)
                ],
                "category": [
                    (category.get("id"), category.get("name"))
                    for category in supplier.get("categories")
                    if category["id"] == category_id
                ],
                "certificates": [
                    {
                        "certificate_name": certificate.get("certificate_name"),
                        "issuing_authority": certificate.get("issuing_authority")
                    }
                    for certificate in supplier.get("certificates")
                ]
            } for supplier in suppliers["items"]
        ]

    except Exception as E:
        result = []
    finally:
        return result


async def get_supplier_cities():
    try:
        suppliers = requests.get(BASE_URL).json()['items']
        cities = sorted({s["city"] for s in suppliers if s.get("city")})
    except Exception:
        cities = []
    finally:
        return cities


async def get_supplier_regions():
    try:
        suppliers = requests.get(BASE_URL).json()['items']
        regions = sorted({s["region"] for s in suppliers if s.get("region")})
    except Exception:
        regions = []
    finally:
        return regions

    
async def main():
    result = await get_supplier_regions()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
