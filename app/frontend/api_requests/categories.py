import requests
import os
from requests.exceptions import ConnectionError, Timeout
from .exceptions import ApiError


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "categories/"


def get_categories():
    try:
        categories = requests.get(BASE_URL + "root", timeout=10).json()
    except ConnectionError:
        raise ApiError("Не удалось подключиться к серверу. Запущен ли бекенд?")
    except Timeout:
        raise ApiError("Сервер не ответил вовремя. Попробуйте позже.")
    except Exception as e:
        raise ApiError(f"Ошибка загрузки категорий: {e}")
    return {
        category.get("id", ""): {
            "name": category.get("name", ""),
            "children": category.get("children") or []
        } for category in categories
    }


if __name__ == "__main__":
    result = get_categories()
    print(result)
