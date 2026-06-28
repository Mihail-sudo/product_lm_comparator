def test_get_all_categories(client):
    resp = client.get("/categories/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    names = [c["name"] for c in data]
    assert "Сырье" in names
    assert "Мука" in names
    assert "Упаковка" in names


def test_get_root_categories(client):
    resp = client.get("/categories/root")
    assert resp.status_code == 200
    data = resp.json()
    names = [c["name"] for c in data]
    assert "Сырье" in names
    assert "Упаковка" in names
    assert "Мука" not in names


def test_get_subcategories(client):
    resp = client.get("/categories/1/subcategories")
    assert resp.status_code == 200
    data = resp.json()
    names = [c["name"] for c in data]
    assert "Мука" in names


def test_get_category_by_id(client):
    resp = client.get("/categories/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Сырье"


def test_get_category_not_found(client):
    resp = client.get("/categories/999")
    assert resp.status_code == 404


def test_create_category(client):
    payload = {"name": "Тестовая категория", "description": "Описание"}
    resp = client.post("/categories/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Тестовая категория"


def test_get_categories_with_count(client):
    resp = client.get("/categories/with-count")
    assert resp.status_code == 200
    data = resp.json()
    for cat in data:
        assert "supplier_count" in cat
    сырье = next(c for c in data if c["name"] == "Сырье")
    assert сырье["supplier_count"] >= 1
