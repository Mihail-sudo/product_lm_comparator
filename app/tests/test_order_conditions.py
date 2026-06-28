def test_get_order_conditions_empty(client):
    resp = client.get("/suppliers/1/order-conditions/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_create_order_condition(client):
    payload = {
        "min_order_quantity": 100,
        "min_order_unit": "kg",
        "price_per_unit": 50.0,
        "price_currency": "RUB",
        "delivery_terms": "Самовывоз",
        "payment_terms": "100% предоплата",
        "lead_time_days": 5,
    }
    resp = client.post("/suppliers/1/order-conditions/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["min_order_quantity"]) == 100
    assert data["supplier_id"] == 1


def test_update_order_condition(client):
    payload = {
        "min_order_quantity": 200,
        "min_order_unit": "kg",
        "price_per_unit": 45.0,
    }
    create = client.post("/suppliers/1/order-conditions/", json=payload)
    condition_id = create.json()["id"]

    update_payload = {"price_per_unit": 40.0, "lead_time_days": 3}
    resp = client.put(f"/suppliers/1/order-conditions/{condition_id}", json=update_payload)
    assert resp.status_code == 200
    assert float(resp.json()["price_per_unit"]) == 40.0


def test_update_order_condition_not_found(client):
    payload = {"min_order_quantity": 100, "min_order_unit": "kg"}
    resp = client.put("/suppliers/1/order-conditions/999", json=payload)
    assert resp.status_code == 404


def test_delete_order_condition(client):
    payload = {"min_order_quantity": 100, "min_order_unit": "kg"}
    create = client.post("/suppliers/1/order-conditions/", json=payload)
    condition_id = create.json()["id"]

    resp = client.delete(f"/suppliers/1/order-conditions/{condition_id}")
    assert resp.status_code == 204

    resp = client.get(f"/suppliers/1/order-conditions/")
    assert resp.json() == []


def test_delete_order_condition_not_found(client):
    resp = client.delete("/suppliers/1/order-conditions/999")
    assert resp.status_code == 404
