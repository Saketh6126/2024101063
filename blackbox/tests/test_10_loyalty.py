"""
test_10_loyalty.py
------------------
L-01 to L-04: Loyalty point schema and redemption tests.
"""

import pytest
from conftest import get, post


class TestLoyalty:

    def test_L01_get_loyalty_schema(self):
        """L-01: GET /loyalty → 200 with loyalty points field."""
        r = get("/loyalty")
        assert r.status_code == 200
        data = r.json()
        has_points = "loyalty_points" in data or "points" in data
        assert has_points, f"No points key in loyalty response: {list(data.keys())}"

    def test_L02_redeem_zero_returns_400(self):
        """L-02: Redeem 0 points → 400."""
        r = post("/loyalty/redeem", {"points": 0})
        assert r.status_code == 400

    def test_L03_redeem_more_than_owned_returns_400(self):
        """L-03: Redeem more than owned → 400."""
        data = get("/loyalty").json()
        pts = data.get("loyalty_points") or data.get("points", 0)
        r = post("/loyalty/redeem", {"points": pts + 999999})
        assert r.status_code == 400

    def test_L04_redeem_valid_points(self):
        """L-04: Redeem 1 point (if available) → 200."""
        data = get("/loyalty").json()
        pts = data.get("loyalty_points") or data.get("points", 0)
        if pts < 1:
            pytest.skip("User has no loyalty points to redeem")
        r = post("/loyalty/redeem", {"points": 1})
        assert r.status_code == 200
