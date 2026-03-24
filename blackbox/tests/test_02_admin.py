"""
test_02_admin.py
----------------
A-01 to A-09: Admin / Data Inspection endpoint tests.
"""

from conftest import get, HEADERS, USER_ID


class TestAdmin:

    def test_A01_get_users_schema(self):
        """A-01: GET /admin/users returns list with correct user schema."""
        r = get("/admin/users", headers=HEADERS)
        assert r.status_code == 200
        users = r.json()
        assert isinstance(users, list)
        assert len(users) > 0
        u = users[0]
        for key in ("user_id", "name", "email", "phone", "wallet_balance", "loyalty_points"):
            assert key in u, f"Missing key '{key}' in user object"

    def test_A02_get_specific_user(self):
        """A-02: GET /admin/users/{id} returns correct user."""
        r = get(f"/admin/users/{USER_ID}", headers=HEADERS)
        assert r.status_code == 200
        assert r.json()["user_id"] == USER_ID

    def test_A03_get_nonexistent_user_returns_404(self):
        """A-03: GET /admin/users/999999 → 404."""
        r = get("/admin/users/999999", headers=HEADERS)
        assert r.status_code == 404

    def test_A04_get_products_schema_includes_inactive(self):
        """A-04: GET /admin/products returns all products including inactive, with correct schema."""
        r = get("/admin/products", headers=HEADERS)
        assert r.status_code == 200
        products = r.json()
        assert isinstance(products, list)
        assert len(products) > 0
        p = products[0]
        for key in ("product_id", "name", "category", "price", "stock_quantity", "is_active"):
            assert key in p, f"Missing key '{key}' in product object"

    def test_A05_get_carts(self):
        """A-05: GET /admin/carts returns 200 with a list."""
        r = get("/admin/carts", headers=HEADERS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_A06_get_orders(self):
        """A-06: GET /admin/orders returns 200 with a list."""
        r = get("/admin/orders", headers=HEADERS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_A07_get_coupons(self):
        """A-07: GET /admin/coupons returns 200 with a list."""
        r = get("/admin/coupons", headers=HEADERS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_A08_get_tickets(self):
        """A-08: GET /admin/tickets returns 200 with a list."""
        r = get("/admin/tickets", headers=HEADERS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_A09_get_addresses(self):
        """A-09: GET /admin/addresses returns 200 with a list."""
        r = get("/admin/addresses", headers=HEADERS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
