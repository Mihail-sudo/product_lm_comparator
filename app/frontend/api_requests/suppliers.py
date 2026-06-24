import requests
import os
import asyncio


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "suppliers/"


async def get_suppliers_by_filter(city=None, region=None, category_id=None):
    params = {
        "category_id": category_id,
        "city": city,
        "region": region
    }
    try: 
        suppliers = requests.get(BASE_URL + "search", params=params).json()
    except Exception as E:
        suppliers = []
    finally:
        return suppliers


async def get_supplier_cities():
    try:
        suppliers = requests.get(BASE_URL).json()['items']
        cities = set(supplier.get("city") for supplier in suppliers)
    except Exception as E:
        cities = set()
    finally:
        return cities


async def get_supplier_regions():
    try:
        suppliers = requests.get(BASE_URL).json()['items']
        regions = set(supplier.get("region") for supplier in suppliers)
    except Exception as E:
        regions = set()
    finally:
        return regions

    
async def main():
    result = await get_supplier_regions()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())