import requests
import os
import asyncio
import pprint


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "comparison/"


async def get_compare_suppliers(ids):
    try:
        suppliers = requests.post(BASE_URL, json={
            "supplier_ids": ids
        }).json()
    except Exception as E:
        print(E)
        suppliers = []
    finally:
        return suppliers


if __name__ == "__main__":
    a = asyncio.run(get_compare_suppliers([1, 2]))
    pprint.pprint(a)
