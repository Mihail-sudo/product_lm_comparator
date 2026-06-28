def test_get_certificates(client):
    resp = client.get("/suppliers/1/certificates/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["certificate_name"] == "ISO 9001"


def test_get_certificates_empty(client):
    resp = client.get("/suppliers/2/certificates/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_get_valid_certificates(client):
    resp = client.get("/suppliers/1/certificates/?only_valid=true")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for cert in data:
        assert cert["is_valid"] is True


def test_create_certificate(client):
    payload = {
        "certificate_name": "ISO 14001",
        "certificate_type": "quality",
        "issuing_authority": "Тестовый орган",
        "is_valid": True,
    }
    resp = client.post("/suppliers/1/certificates/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["certificate_name"] == "ISO 14001"
    assert data["supplier_id"] == 1
    assert data["id"] is not None


def test_update_certificate(client):
    payload = {
        "certificate_name": "ISO 9001 (обновлено)",
        "certificate_type": "iso",
        "is_valid": True,
    }
    resp = client.put("/suppliers/1/certificates/1", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["certificate_name"] == "ISO 9001 (обновлено)"


def test_update_certificate_not_found(client):
    payload = {"certificate_name": "Тест", "certificate_type": "iso"}
    resp = client.put("/suppliers/1/certificates/999", json=payload)
    assert resp.status_code == 404


def test_delete_certificate(client):
    resp = client.delete("/suppliers/1/certificates/1")
    assert resp.status_code == 204


def test_delete_certificate_not_found(client):
    resp = client.delete("/suppliers/1/certificates/999")
    assert resp.status_code == 404
