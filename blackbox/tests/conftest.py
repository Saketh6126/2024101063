"""
conftest.py
-----------
Shared fixtures and helpers for all QuickCart test modules.
"""

import pytest
import requests

BASE         = "http://localhost:8080/api/v1"
ROLL         = "2024101063"
USER_ID      = 2

HEADERS      = {"X-Roll-Number": ROLL}
USER_HEADERS = {"X-Roll-Number": ROLL, "X-User-ID": str(USER_ID)}


# ── HTTP helpers ────────────────────────────────────────────────────────────

def get(path, headers=None):
    return requests.get(BASE + path, headers=headers or USER_HEADERS)

def post(path, body=None, headers=None):
    return requests.post(BASE + path, json=body, headers=headers or USER_HEADERS)

def put(path, body=None, headers=None):
    return requests.put(BASE + path, json=body, headers=headers or USER_HEADERS)

def delete(path, headers=None):
    return requests.delete(BASE + path, headers=headers or USER_HEADERS)


# ── Shared fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(autouse=False)
def empty_cart():
    """Ensure cart is clear before and after each test that uses it."""
    delete("/cart/clear")
    yield
    delete("/cart/clear")


@pytest.fixture
def cheapest_product():
    """Return the cheapest active product dict."""
    products = get("/products").json()
    if not products:
        pytest.skip("No active products in DB")
    return sorted(products, key=lambda p: p["price"])[0]


@pytest.fixture
def placed_order(cheapest_product, empty_cart):
    """Place a fresh COD order and return its order_id."""
    post("/cart/add", {"product_id": cheapest_product["product_id"], "quantity": 1})
    r = post("/checkout", {"payment_method": "COD"})
    assert r.status_code in (200, 201), f"Could not place order: {r.text}"
    data = r.json()
    order = data.get("order", data)
    oid = order.get("order_id")
    if not oid:
        pytest.skip("Could not extract order_id from checkout response")
    return oid
