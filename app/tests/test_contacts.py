def test_get_contacts(client):
    resp = client.get("/suppliers/1/contacts/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["contact_type"] == "phone"
    assert data[0]["contact_value"] == "+7-495-123-45-67"


def test_get_contacts_empty(client):
    resp = client.get("/suppliers/2/contacts/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_get_primary_contact(client):
    resp = client.get("/suppliers/1/contacts/primary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_primary"] is True


def test_create_contact(client):
    payload = {
        "contact_type": "email",
        "contact_value": "test@supplier.ru",
        "contact_person": "Петр Петров",
        "is_primary": False,
    }
    resp = client.post("/suppliers/1/contacts/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["contact_value"] == "test@supplier.ru"
    assert data["supplier_id"] == 1


def test_update_contact(client):
    payload = {"contact_value": "+7-495-999-99-99", "contact_type": "phone"}
    resp = client.put("/suppliers/1/contacts/1", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["contact_value"] == "+7-495-999-99-99"


def test_delete_contact(client):
    resp = client.delete("/suppliers/1/contacts/1")
    assert resp.status_code == 204

    resp = client.get("/suppliers/1/contacts/")
    assert resp.json() == []


def test_delete_contact_not_found(client):
    resp = client.delete("/suppliers/1/contacts/999")
    assert resp.status_code == 404
