import pytest
import uuid
from fastapi.testclient import TestClient
from api.main import app

client     = TestClient(app)
SESSION_ID = f"test-api-{uuid.uuid4()}"


class TestAPI:

    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agents" in data

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "docs" in response.json()

    def test_list_products(self):
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        assert "title" in products[0]
        assert "price" in products[0]

    def test_list_products_with_category_filter(self):
        response = client.get("/api/v1/products?category=machine+learning")
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0

    def test_list_products_with_price_filter(self):
        response = client.get("/api/v1/products?max_price=800")
        assert response.status_code == 200
        for p in response.json():
            assert p["price"] <= 800

    def test_get_product_by_id(self):
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "title" in data

    def test_get_nonexistent_product(self):
        response = client.get("/api/v1/products/9999")
        assert response.status_code == 404

    def test_get_categories(self):
        response = client.get("/api/v1/products/meta/categories")
        assert response.status_code == 200
        assert "categories" in response.json()

    def test_get_price_range(self):
        response = client.get("/api/v1/products/meta/price-range")
        assert response.status_code == 200
        data = response.json()
        assert "min" in data
        assert "max" in data

    def test_place_order(self):
        response = client.post("/api/v1/order", json={
            "product_id": 1,
            "session_id": SESSION_ID
        })
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"].startswith("ORD-")
        assert data["status"] == "confirmed"

    def test_track_order(self):
        # Place order first
        order_response = client.post("/api/v1/order", json={
            "product_id": 1,
            "session_id": SESSION_ID
        })
        order_id = order_response.json()["order_id"]

        # Track it
        response = client.get(f"/api/v1/track/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert "delivery_status" in data
        assert "eta" in data

    def test_track_nonexistent_order(self):
        response = client.get("/api/v1/track/ORD-99999")
        assert response.status_code == 404

    def test_return_order(self):
        order_response = client.post("/api/v1/order", json={
            "product_id": 2,
            "session_id": SESSION_ID
        })
        order_id = order_response.json()["order_id"]

        response = client.post("/api/v1/return", json={
            "order_id":   order_id,
            "reason":     "Wrong item",
            "session_id": SESSION_ID
        })
        assert response.status_code == 200
        data = response.json()
        assert data["return_id"].startswith("RET-")
        assert data["status"] == "initiated"

    def test_get_history_empty(self):
        new_session = f"empty-{uuid.uuid4()}"
        response    = client.get(f"/api/v1/history/{new_session}")
        assert response.status_code == 200
        assert response.json() == []

    def test_clear_history(self):
        response = client.delete(f"/api/v1/history/{SESSION_ID}")
        assert response.status_code == 200
        assert "cleared" in response.json()["message"]
