"""
test_11_orders.py
-----------------
O-01 to O-08: Order listing, single lookup, cancel (valid/delivered/nonexistent),
invoice schema and total match, and stock restoration.
"""

import pytest
from conftest import get, post, delete, HEADERS


def _place_order():
    """Place a fresh COD order and return order_id."""
    products = sorted(get("/products").json(), key=lambda p: p["price"])
    if not products:
        pytest.skip("No active products")
    p = products[0]
    delete("/cart/clear")
    post("/cart/add", {"product_id": p["product_id"], "quantity": 1})
    r = post("/checkout", {"payment_method": "COD"})
    assert r.status_code in (200, 201)
    data = r.json()
    order = data.get("order", data)
    oid = order.get("order_id")
    if not oid:
        pytest.skip("Could not extract order_id")
    return oid, p["product_id"]


class TestOrders:

    def test_O01_get_orders_schema(self):
        """O-01: GET /orders → 200, list with order schema keys."""
        r = get("/orders")
        assert r.status_code == 200
        orders = r.json()
        assert isinstance(orders, list)
        if orders:
            o = orders[0]
            assert "order_id" in o, "Missing 'order_id' in order schema"

    def test_O02_get_single_order(self):
        """O-02: GET /orders/{id} → 200 with correct order_id and items."""
        oid, _ = _place_order()
        r = get(f"/orders/{oid}")
        assert r.status_code == 200
        data = r.json()
        assert data.get("order_id") == oid
        assert "items" in data

    def test_O03_cancel_order(self):
        """O-03: Cancel a fresh (pending) order → 200."""
        oid, _ = _place_order()
        r = post(f"/orders/{oid}/cancel")
        assert r.status_code == 200

    def test_O04_cancel_delivered_order_returns_400(self):
        """O-04: Cancel a DELIVERED order → 400."""
        orders = get("/admin/orders", headers=HEADERS).json()
        delivered = [o for o in orders
                     if o.get("status") == "DELIVERED"
                     or o.get("order_status") == "DELIVERED"]
        if not delivered:
            pytest.skip("No DELIVERED orders in DB")
        # Use an order belonging to our test user if possible. Fall back to any.
        mine = [o for o in delivered if o.get("user_id") == 2]
        target = mine[0] if mine else delivered[0]
        oid = target.get("order_id")
        r = post(f"/orders/{oid}/cancel")
        assert r.status_code == 400, \
            f"Expected 400 for DELIVERED order cancel, got {r.status_code}"

    def test_O05_cancel_nonexistent_order_returns_404(self):
        """O-05: Cancel non-existent order → 404."""
        r = post("/orders/999999/cancel")
        assert r.status_code == 404

    def test_O06_get_invoice_schema(self):
        """O-06: GET /orders/{id}/invoice → 200 with subtotal + total (or total_amount)."""
        oid, _ = _place_order()
        r = get(f"/orders/{oid}/invoice")
        assert r.status_code == 200
        inv = r.json()
        assert "subtotal" in inv, f"Missing 'subtotal' in invoice: {list(inv.keys())}"
        has_total = "total" in inv or "total_amount" in inv
        assert has_total, f"No total key in invoice: {list(inv.keys())}"

    def test_O07_invoice_total_matches_order_total(self):
        """O-07: invoice.total == order.total exactly."""
        oid, _ = _place_order()
        order = get(f"/orders/{oid}").json()
        inv   = get(f"/orders/{oid}/invoice").json()
        order_total = order.get("total") or order.get("total_amount", 0)
        inv_total   = inv.get("total") or inv.get("total_amount", 0)
        assert abs(order_total - inv_total) < 0.01, \
            f"Invoice total {inv_total} != order total {order_total}"

    def test_O08_cancel_restores_stock(self):
        """O-08: Cancelling order restores items back to product stock."""
        oid, pid = _place_order()
        admin_products = get("/admin/products", headers=HEADERS).json()
        stock_before = next(
            (p["stock_quantity"] for p in admin_products if p["product_id"] == pid), None
        )
        order = get(f"/orders/{oid}").json()
        cancelled_qty = next(
            (i["quantity"] for i in order.get("items", []) if i["product_id"] == pid), 1
        )
        post(f"/orders/{oid}/cancel")
        stock_after = next(
            (p["stock_quantity"] for p in get("/admin/products", headers=HEADERS).json()
             if p["product_id"] == pid), None
        )
        assert stock_after == stock_before + cancelled_qty, \
            f"Stock not restored: before={stock_before}, after={stock_after}, qty={cancelled_qty}"
