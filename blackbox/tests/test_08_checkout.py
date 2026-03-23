"""
test_08_checkout.py
-------------------
CH-01 to CH-10: Checkout tests covering all payment modes and GST validation.
"""

import pytest
from conftest import get, post, delete, HEADERS


def _add_cheap_item():
    products = sorted(get("/products").json(), key=lambda p: p["price"])
    if not products:
        pytest.skip("No active products")
    p = products[0]
    delete("/cart/clear")
    post("/cart/add", {"product_id": p["product_id"], "quantity": 1})
    return p


class TestCheckout:

    def setup_method(self):
        delete("/cart/clear")

    def test_CH01_admin_order_schema(self):
        """CH-01: GET /admin/orders → 200, probe schema keys."""
        r = get("/admin/orders", headers=HEADERS)
        assert r.status_code == 200
        orders = r.json()
        assert isinstance(orders, list)
        if orders:
            o = orders[0]
            assert "order_id" in o, "Missing 'order_id' in order schema"

    def test_CH02_checkout_empty_cart_returns_400(self):
        """CH-02: Checkout with empty cart → 400."""
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code == 400

    def test_CH03_invalid_payment_method_returns_400(self):
        """CH-03: payment_method='CRYPTO' → 400."""
        _add_cheap_item()
        r = post("/checkout", {"payment_method": "CRYPTO"})
        assert r.status_code == 400

    def test_CH04_cod_payment_pending_status(self):
        """CH-04: COD checkout → order payment_status = PENDING."""
        _add_cheap_item()
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code in (200, 201)
        data = r.json()
        order = data.get("order", data)
        assert order.get("payment_status") == "PENDING"

    def test_CH05_wallet_payment_pending_status(self):
        """CH-05: WALLET checkout → order payment_status = PENDING."""
        _add_cheap_item()
        post("/wallet/add", {"amount": 5000})
        r = post("/checkout", {"payment_method": "WALLET"})
        assert r.status_code in (200, 201)
        data = r.json()
        order = data.get("order", data)
        assert order.get("payment_status") == "PENDING"

    def test_CH06_card_payment_paid_status(self):
        """CH-06: CARD checkout → order payment_status = PAID."""
        _add_cheap_item()
        r = post("/checkout", {"payment_method": "CARD"})
        assert r.status_code in (200, 201)
        data = r.json()
        order = data.get("order", data)
        assert order.get("payment_status") == "PAID"

    def test_CH07_cod_above_5001_returns_400(self):
        """CH-07: COD with total > 5000 → 400."""
        products = sorted(get("/products").json(), key=lambda p: p["price"], reverse=True)
        if not products:
            pytest.skip("No active products")
        p = products[0]
        qty = max(1, int(5001 / p["price"]) + 1)
        post("/cart/add", {"product_id": p["product_id"], "quantity": qty})
        cart_total = get("/cart").json()["total"]
        if cart_total <= 5000:
            pytest.skip("Could not exceed 5000 with available products")
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code == 400

    def _gst_check(self, payment_method):
        _add_cheap_item()
        if payment_method == "WALLET":
            post("/wallet/add", {"amount": 5000})
        r = post("/checkout", {"payment_method": payment_method})
        assert r.status_code in (200, 201)
        data = r.json()
        order = data.get("order", data)
        oid = order.get("order_id")
        if not oid:
            pytest.skip("Could not get order_id")
        inv = get(f"/orders/{oid}/invoice").json()
        subtotal = inv.get("subtotal")
        total    = inv.get("total")
        if subtotal and total:
            assert abs(total - subtotal * 1.05) < 0.5, \
                f"GST wrong for {payment_method}: subtotal={subtotal}, total={total}"

    def test_CH08_gst_5_percent_cod(self):
        """CH-08: Invoice total = subtotal × 1.05 for COD."""
        self._gst_check("COD")

    def test_CH09_gst_5_percent_wallet(self):
        """CH-09: Invoice total = subtotal × 1.05 for WALLET."""
        self._gst_check("WALLET")

    def test_CH10_gst_5_percent_card(self):
        """CH-10: Invoice total = subtotal × 1.05 for CARD."""
        self._gst_check("CARD")
