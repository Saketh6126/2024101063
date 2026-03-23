"""
test_05_products.py
-------------------
PR-01 to PR-08: Product listing, filtering, and lookup tests.
Note: Query param names (category, search, sort) probed from the API itself.
"""

import pytest
from conftest import get, HEADERS


class TestProducts:

    def test_PR01_active_products_only_and_schema(self):
        """PR-01: GET /products returns only active products; verify none are inactive."""
        r = get("/products")
        assert r.status_code == 200
        public = r.json()
        assert isinstance(public, list)

        admin = get("/admin/products", headers=HEADERS).json()
        inactive_ids = {p["product_id"] for p in admin if not p.get("is_active")}
        public_ids   = {p["product_id"] for p in public}
        assert public_ids.isdisjoint(inactive_ids), \
            f"Inactive products found in public list: {public_ids & inactive_ids}"

    def test_PR02_price_matches_db_exactly(self):
        """PR-02: Price in public list must match admin DB exactly (no rounding)."""
        public = get("/products").json()
        admin  = {p["product_id"]: p for p in get("/admin/products", headers=HEADERS).json()}
        for p in public:
            pid = p["product_id"]
            assert p["price"] == admin[pid]["price"], \
                f"Price mismatch for product {pid}: got {p['price']}, expected {admin[pid]['price']}"

    def test_PR03_get_product_by_id(self):
        """PR-03: GET /products/{id} returns correct product."""
        products = get("/products").json()
        if not products:
            pytest.skip("No active products")
        pid = products[0]["product_id"]
        r = get(f"/products/{pid}")
        assert r.status_code == 200
        assert r.json()["product_id"] == pid

    def test_PR04_nonexistent_product_returns_404(self):
        """PR-04: GET /products/999999 → 404."""
        r = get("/products/999999")
        assert r.status_code == 404

    def test_PR05_filter_by_category(self):
        """PR-05: Filter products by category=Fruits."""
        r = get("/products?category=Fruits")
        assert r.status_code == 200
        for p in r.json():
            assert p["category"] == "Fruits", \
                f"Product {p['product_id']} has category '{p['category']}', expected 'Fruits'"

    def test_PR06_search_by_name(self):
        """PR-06: Search products by name containing 'Apple'."""
        r = get("/products?search=Apple")
        assert r.status_code == 200
        for p in r.json():
            assert "apple" in p["name"].lower(), \
                f"Product name '{p['name']}' doesn't match search 'Apple'"

    def test_PR07_sort_price_ascending(self):
        """PR-07: Sort products by price ascending."""
        r = get("/products?sort=price_asc")
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices), "Products are not sorted in ascending price order"

    def test_PR08_sort_price_descending(self):
        """PR-08: Sort products by price descending."""
        r = get("/products?sort=price_desc")
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices, reverse=True), \
            "Products are not sorted in descending price order"
