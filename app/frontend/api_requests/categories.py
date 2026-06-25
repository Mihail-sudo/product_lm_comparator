import requests
import os
import asyncio


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "categories/"


async def get_categories():
    try: 
        categories = requests.get(BASE_URL + "root").json()
        categories = {
            category.get("id", ""): {
                "name": category.get("name", ""),
                "children": category.get("children", [{}])
            } for category in categories}
    except Exception as E:
        categories = {}
    finally:
        return categories


async def main():
    result = await get_categories()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
