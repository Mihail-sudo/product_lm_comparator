def test_get_suppliers_list(client):
    resp = client.get("/suppliers/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2
    assert data["skip"] == 0
    assert data["limit"] == 50


def test_get_suppliers_list_only_active(client):
    resp = client.get("/suppliers/?only_active=true")
    assert resp.status_code == 200
    data = resp.json()
    names = [s["name"] for s in data["items"]]
    assert "ООО Тест" not in names
    assert "ООО Поставщик" in names


def test_get_suppliers_list_pagination(client):
    resp = client.get("/suppliers/?skip=0&limit=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["total"] >= 2


def test_get_supplier_by_id(client):
    resp = client.get("/suppliers/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "ООО Поставщик"
    assert data["city"] == "Москва"
    assert data["is_verified"] is True
    assert len(data["categories"]) >= 1
    assert len(data["contacts"]) >= 1
    assert len(data["certificates"]) >= 1


def test_get_supplier_not_found(client):
    resp = client.get("/suppliers/999")
    assert resp.status_code == 404


def test_search_suppliers_by_city(client):
    resp = client.get("/suppliers/search?city=Москва")
    assert resp.status_code == 200
    data = resp.json()
    names = [s["name"] for s in data["items"]]
    assert "ООО Поставщик" in names
    assert "ИП Производитель" not in names


def test_search_suppliers_by_rating(client):
    resp = client.get("/suppliers/search?min_rating=4.0")
    assert resp.status_code == 200
    data = resp.json()
    names = [s["name"] for s in data["items"]]
    assert "ООО Поставщик" in names
    assert "ИП Производитель" not in names


def test_search_suppliers_verified(client):
    resp = client.get("/suppliers/search?is_verified=true")
    assert resp.status_code == 200
    data = resp.json()
    names = [s["name"] for s in data["items"]]
    assert "ООО Поставщик" in names
    assert "ИП Производитель" not in names


def test_search_suppliers_pagination(client):
    resp = client.get("/suppliers/search?skip=0&limit=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["total"] >= 2


def test_create_supplier(client):
    payload = {
        "name": "Новый поставщик",
        "city": "Санкт-Петербург",
        "description": "Тестовый поставщик",
        "region": "Северо-Западный",
        "is_verified": False,
        "status": "active",
    }
    resp = client.post("/suppliers/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Новый поставщик"
    assert data["city"] == "Санкт-Петербург"
    assert data["id"] is not None


def test_create_supplier_validation_error(client):
    payload = {"name": "x" * 300}
    resp = client.post("/suppliers/", json=payload)
    assert resp.status_code == 422


def test_update_supplier(client):
    payload = {"name": "ООО Поставщик (обновлено)", "rating": 5.0}
    resp = client.put("/suppliers/1", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "ООО Поставщик (обновлено)"


def test_update_supplier_not_found(client):
    resp = client.put("/suppliers/999", json={"name": "Тест"})
    assert resp.status_code == 404


def test_delete_supplier(client):
    resp = client.delete("/suppliers/2")
    assert resp.status_code == 204

    resp = client.get("/suppliers/2")
    assert resp.status_code == 404


def test_delete_supplier_not_found(client):
    resp = client.delete("/suppliers/999")
    assert resp.status_code == 404


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert "docs" in data
