"""
test_06_cart.py
---------------
C-01 to C-14: Cart management tests.
"""

import pytest
from conftest import get, post, delete, HEADERS


def _first_product():
    products = get("/products").json()
    if not products:
        pytest.skip("No active products available")
    return products[0]


def _product_with_low_stock():
    admin = get("/admin/products", headers=HEADERS).json()
    active = [p for p in admin if p.get("is_active") and p.get("stock_quantity", 0) > 0]
    if not active:
        pytest.skip("No active products with stock")
    return min(active, key=lambda p: p["stock_quantity"])


class TestCart:

    def setup_method(self):
        delete("/cart/clear")

    def teardown_method(self):
        delete("/cart/clear")

    def test_C01_get_cart_schema(self):
        """C-01: GET /cart → 200 with cart_id, items, total."""
        r = get("/cart")
        assert r.status_code == 200
        data = r.json()
        for key in ("cart_id", "items", "total"):
            assert key in data, f"Missing key '{key}' in cart"

    def test_C02_add_valid_item(self):
        """C-02: Add valid product with qty=1 → 200/201."""
        p = _first_product()
        r = post("/cart/add", {"product_id": p["product_id"], "quantity": 1})
        assert r.status_code in (200, 201)

    def test_C03_add_zero_quantity_returns_400(self):
        """C-03: qty=0 → 400."""
        p = _first_product()
        r = post("/cart/add", {"product_id": p["product_id"], "quantity": 0})
        assert r.status_code == 400

    def test_C04_add_negative_quantity_returns_400(self):
        """C-04: qty=-1 → 400."""
        p = _first_product()
        r = post("/cart/add", {"product_id": p["product_id"], "quantity": -1})
        assert r.status_code == 400

    def test_C05_add_nonexistent_product_returns_404(self):
        """C-05: product_id=999999 → 404."""
        r = post("/cart/add", {"product_id": 999999, "quantity": 1})
        assert r.status_code == 404

    def test_C06_add_over_stock_returns_400(self):
        """C-06: qty > stock_quantity → 400."""
        p = _product_with_low_stock()
        over_qty = p["stock_quantity"] + 1
        r = post("/cart/add", {"product_id": p["product_id"], "quantity": over_qty})
        assert r.status_code == 400

    def test_C07_add_same_product_twice_accumulates(self):
        """C-07: Adding same product twice accumulates quantities (1+2=3)."""
        p = _first_product()
        post("/cart/add", {"product_id": p["product_id"], "quantity": 1})
        post("/cart/add", {"product_id": p["product_id"], "quantity": 2})
        cart = get("/cart").json()
        item = next((i for i in cart["items"] if i["product_id"] == p["product_id"]), None)
        assert item is not None
        assert item["quantity"] == 3, f"Expected qty=3, got {item['quantity']}"

    def test_C08_subtotal_is_qty_times_price(self):
        """C-08: subtotal = quantity × price for each item."""
        p = _first_product()
        post("/cart/add", {"product_id": p["product_id"], "quantity": 3})
        cart = get("/cart").json()
        item = next((i for i in cart["items"] if i["product_id"] == p["product_id"]), None)
        assert item is not None
        unit_price = item.get("price") or item.get("unit_price")
        subtotal   = item.get("subtotal") or item.get("item_total")
        assert unit_price is not None, f"No price key in cart item: {list(item.keys())}"
        assert subtotal is not None, f"No subtotal key in cart item: {list(item.keys())}"
        expected = item["quantity"] * unit_price
        assert abs(subtotal - expected) < 0.01, \
            f"Subtotal mismatch: got {subtotal}, expected {expected}"

    def test_C09_cart_total_is_sum_of_subtotals(self):
        """C-09: cart.total = sum of all item subtotals."""
        products = get("/products").json()
        if len(products) < 2:
            pytest.skip("Need at least 2 products")
        for p in products[:2]:
            post("/cart/add", {"product_id": p["product_id"], "quantity": 2})
        cart = get("/cart").json()
        expected_total = sum(
            (i.get("subtotal") or i.get("item_total", 0))
            for i in cart["items"]
        )
        assert abs(cart["total"] - expected_total) < 0.01, \
            f"Cart total mismatch: got {cart['total']}, expected {expected_total}"

    def test_C10_update_cart_boundary_qty_1(self):
        """C-10: update with qty=1 (boundary minimum) → 200."""
        p = _first_product()
        post("/cart/add", {"product_id": p["product_id"], "quantity": 2})
        r = post("/cart/update", {"product_id": p["product_id"], "quantity": 1})
        assert r.status_code == 200

    def test_C11_update_cart_zero_quantity_returns_400(self):
        """C-11: update qty=0 → 400."""
        p = _first_product()
        post("/cart/add", {"product_id": p["product_id"], "quantity": 2})
        r = post("/cart/update", {"product_id": p["product_id"], "quantity": 0})
        assert r.status_code == 400

    def test_C12_remove_item_from_cart(self):
        """C-12: Remove existing item → 200."""
        p = _first_product()
        post("/cart/add", {"product_id": p["product_id"], "quantity": 1})
        r = post("/cart/remove", {"product_id": p["product_id"]})
        assert r.status_code == 200

    def test_C13_remove_nonexistent_item_returns_404(self):
        """C-13: Remove product not in cart → 404."""
        r = post("/cart/remove", {"product_id": 999999})
        assert r.status_code == 404

    def test_C14_clear_cart(self):
        """C-14: DELETE /cart/clear → cart empty (items=[], total=0)."""
        p = _first_product()
        post("/cart/add", {"product_id": p["product_id"], "quantity": 1})
        rd = delete("/cart/clear")
        assert rd.status_code in (200, 204)
        cart = get("/cart").json()
        assert cart["items"] == []
        assert cart["total"] == 0
