"""
test_07_coupons.py
------------------
CU-01 to CU-08: Coupon schema probe and validation tests.
"""

import pytest
from conftest import get, post, delete, HEADERS


def _load_cart():
    products = get("/products").json()
    if not products:
        pytest.skip("No active products")
    delete("/cart/clear")
    for p in products[:2]:
        post("/cart/add", {"product_id": p["product_id"], "quantity": 3})


class TestCoupons:

    def test_CU01_schema_probe(self):
        """CU-01: GET /admin/coupons → 200 with coupon schema keys."""
        r = get("/admin/coupons", headers=HEADERS)
        assert r.status_code == 200
        coupons = r.json()
        assert isinstance(coupons, list)
        if coupons:
            c = coupons[0]
            # Probe actual key name — could be 'code' or 'coupon_code'
            has_code = "code" in c or "coupon_code" in c
            assert has_code, f"No code key found in coupon schema: {list(c.keys())}"

    def _code(self, c):
        return c.get("code") or c.get("coupon_code")

    def _min_val(self, c):
        return c.get("min_cart_value") or c.get("minimum_cart_value") or c.get("minimum_order_value", 0)

    def _is_expired(self, c):
        return c.get("is_expired") or c.get("expired") or False

    def _max_cap(self, c):
        return c.get("max_discount") or c.get("maximum_discount") or c.get("max_discount_amount")

    def test_CU02_expired_coupon_returns_400(self):
        """CU-02: Applying an expired coupon → 400."""
        coupons = get("/admin/coupons", headers=HEADERS).json()
        expired = [c for c in coupons if self._is_expired(c)]
        if not expired:
            pytest.skip("No expired coupons in DB")
        _load_cart()
        r = post("/coupon/apply", {"code": self._code(expired[0])})
        assert r.status_code == 400

    def test_CU03_cart_below_min_value_returns_400(self):
        """CU-03: Cart total < coupon's min_cart_value → 400."""
        coupons = get("/admin/coupons", headers=HEADERS).json()
        valid = [c for c in coupons
                 if not self._is_expired(c) and self._min_val(c) > 0]
        if not valid:
            pytest.skip("No coupon with min_cart_value found")
        delete("/cart/clear")
        r = post("/coupon/apply", {"code": self._code(valid[0])})
        assert r.status_code == 400

    def test_CU04_percent_coupon_discount_calculation(self):
        """CU-04: PERCENT coupon applies percent off correctly."""
        coupons = get("/admin/coupons", headers=HEADERS).json()
        percent_coupons = [c for c in coupons
                           if not self._is_expired(c)
                           and c.get("discount_type") == "PERCENT"]
        if not percent_coupons:
            pytest.skip("No active PERCENT coupons in DB")
        _load_cart()
        coupon = percent_coupons[0]
        cart_total = get("/cart").json()["total"]
        if cart_total < self._min_val(coupon):
            pytest.skip("Cart total below coupon minimum")
        r = post("/coupon/apply", {"code": self._code(coupon)})
        assert r.status_code == 200
        discount_val = coupon.get("discount_value") or coupon.get("discount_percent", 0)
        expected_discount = cart_total * discount_val / 100
        cap = self._max_cap(coupon)
        if cap:
            expected_discount = min(expected_discount, cap)
        data = r.json()
        actual_discount = data.get("discount") or data.get("discount_amount")
        if actual_discount is not None:
            assert abs(actual_discount - expected_discount) < 0.01, \
                f"PERCENT discount wrong: got {actual_discount}, expected {expected_discount}"

    def test_CU05_fixed_coupon_discount_calculation(self):
        """CU-05: FIXED coupon applies flat amount off correctly."""
        coupons = get("/admin/coupons", headers=HEADERS).json()
        fixed_coupons = [c for c in coupons
                         if not self._is_expired(c)
                         and c.get("discount_type") == "FIXED"]
        if not fixed_coupons:
            pytest.skip("No active FIXED coupons in DB")
        _load_cart()
        coupon = fixed_coupons[0]
        cart_total = get("/cart").json()["total"]
        if cart_total < self._min_val(coupon):
            pytest.skip("Cart total below coupon minimum")
        r = post("/coupon/apply", {"code": self._code(coupon)})
        assert r.status_code == 200
        expected_discount = coupon.get("discount_value") or coupon.get("discount_amount", 0)
        cap = self._max_cap(coupon)
        if cap:
            expected_discount = min(expected_discount, cap)
        data = r.json()
        actual_discount = data.get("discount") or data.get("discount_amount")
        if actual_discount is not None:
            assert abs(actual_discount - expected_discount) < 0.01, \
                f"FIXED discount wrong: got {actual_discount}, expected {expected_discount}"

    def test_CU06_max_discount_cap_enforced(self):
        """CU-06: Discount must not exceed max_discount cap."""
        coupons = get("/admin/coupons", headers=HEADERS).json()
        capped = [c for c in coupons
                  if not self._is_expired(c) and self._max_cap(c)]
        if not capped:
            pytest.skip("No coupons with max_discount in DB")
        _load_cart()
        coupon = capped[0]
        max_cap = self._max_cap(coupon)
        r = post("/coupon/apply", {"code": self._code(coupon)})
        if r.status_code != 200:
            pytest.skip("Coupon conditions not met with current cart")
        data = r.json()
        actual_discount = data.get("discount") or data.get("discount_amount")
        if actual_discount is not None:
            assert actual_discount <= max_cap + 0.01, \
                f"Discount {actual_discount} exceeds max cap {max_cap}"

    def test_CU07_invalid_coupon_code_returns_error(self):
        """CU-07: Applying non-existent coupon code → 400 or 404."""
        _load_cart()
        r = post("/coupon/apply", {"code": "TOTALLYINVALIDXYZ999"})
        assert r.status_code in (400, 404)

    def test_CU08_remove_coupon(self):
        """CU-08: POST /coupon/remove → 200 or 400 (graceful)."""
        r = post("/coupon/remove")
        assert r.status_code in (200, 400)
