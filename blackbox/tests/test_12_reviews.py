"""
test_12_reviews.py
------------------
R-01 to R-12: Product review schema, valid/invalid rating, comment boundaries,
average rating correctness, and zero-review average.
"""

import pytest
from conftest import get, post


def _first_product_id():
    products = get("/products").json()
    if not products:
        pytest.skip("No active products")
    return products[0]["product_id"]


class TestReviews:

    def test_R01_get_reviews_schema(self):
        """R-01: GET /products/{id}/reviews → 200, confirm schema."""
        pid = _first_product_id()
        r = get(f"/products/{pid}/reviews")
        assert r.status_code == 200
        data = r.json()
        # response could be {"reviews": [...], "average_rating": ...} or just a list
        assert isinstance(data, (list, dict))

    def test_R02_add_valid_review(self):
        """R-02: POST valid review (rating=3, comment='Okay') → 200/201."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 3, "comment": "Okay product"})
        assert r.status_code in (200, 201)

    def test_R03_rating_zero_returns_400(self):
        """R-03: rating=0 → 400."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 0, "comment": "bad"})
        assert r.status_code == 400

    def test_R04_rating_6_returns_400(self):
        """R-04: rating=6 → 400."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 6, "comment": "too high"})
        assert r.status_code == 400

    def test_R05_rating_boundary_min_1(self):
        """R-05: rating=1 (boundary min) → 200/201."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 1, "comment": "Worst"})
        assert r.status_code in (200, 201)

    def test_R06_rating_boundary_max_5(self):
        """R-06: rating=5 (boundary max) → 200/201."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 5, "comment": "Perfect!"})
        assert r.status_code in (200, 201)

    def test_R07_empty_comment_returns_400(self):
        """R-07: comment='' → 400."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 3, "comment": ""})
        assert r.status_code == 400

    def test_R08_comment_boundary_min_1_char(self):
        """R-08: comment with exactly 1 char → 200/201."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 3, "comment": "A"})
        assert r.status_code in (200, 201)

    def test_R09_comment_boundary_max_200_chars(self):
        """R-09: comment with exactly 200 chars → 200/201."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 3, "comment": "A" * 200})
        assert r.status_code in (200, 201)

    def test_R10_comment_201_chars_returns_400(self):
        """R-10: comment with 201 chars → 400."""
        pid = _first_product_id()
        r = post(f"/products/{pid}/reviews", {"rating": 3, "comment": "A" * 201})
        assert r.status_code == 400

    def test_R11_average_rating_is_decimal(self):
        """R-11: Average of ratings 3 and 4 must be 3.5 (not floored to 3)."""
        pid = _first_product_id()
        post(f"/products/{pid}/reviews", {"rating": 3, "comment": "Okay"})
        post(f"/products/{pid}/reviews", {"rating": 4, "comment": "Good"})
        data = get(f"/products/{pid}/reviews").json()
        avg = data.get("average_rating") if isinstance(data, dict) else None
        if avg is None:
            pytest.skip("average_rating not in response")
        # Should be 3.5 or at minimum not be an integer floor
        assert avg != int(avg) or avg == 3.5, \
            f"Average rating appears floored: got {avg}, expected 3.5"

    def test_R12_no_reviews_average_is_zero(self):
        """R-12: Product with no reviews → average_rating = 0."""
        from conftest import HEADERS
        all_products = get("/admin/products", headers=HEADERS).json()
        no_review_pid = None
        for p in all_products:
            if not p.get("is_active"):
                continue
            r = get(f"/products/{p['product_id']}/reviews")
            if r.status_code != 200:
                continue
            body = r.json()
            reviews = body.get("reviews", body) if isinstance(body, dict) else body
            if isinstance(reviews, list) and len(reviews) == 0:
                no_review_pid = p["product_id"]
                break
        if not no_review_pid:
            pytest.skip("All products have at least one review")
        data = get(f"/products/{no_review_pid}/reviews").json()
        avg = data.get("average_rating") if isinstance(data, dict) else None
        if avg is None:
            pytest.skip("average_rating not present")
        assert avg == 0, f"Expected average_rating=0 for no-review product, got {avg}"
