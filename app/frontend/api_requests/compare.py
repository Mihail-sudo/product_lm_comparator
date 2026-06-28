import requests
import os
import pprint
from requests.exceptions import ConnectionError, Timeout
from .exceptions import ApiError


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/") + "comparison/"


def get_compare_suppliers(ids):
    try:
        resp = requests.post(BASE_URL, json={"supplier_ids": ids}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except ConnectionError:
        raise ApiError("Не удалось подключиться к серверу. Запущен ли бекенд (порт 8000)?")
    except Timeout:
        raise ApiError("Сервер не ответил вовремя. Попробуйте позже.")
    except requests.exceptions.HTTPError as e:
        raise ApiError(f"Сервер вернул ошибку: {e}")


if __name__ == "__main__":
    a = get_compare_suppliers([1, 2])
    pprint.pprint(a)
