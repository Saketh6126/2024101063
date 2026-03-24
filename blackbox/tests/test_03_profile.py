"""
test_03_profile.py
------------------
P-01 to P-09: Profile GET and PUT tests.
"""

from conftest import get, put


class TestProfile:

    def test_P01_get_profile_schema(self):
        """P-01: GET /profile returns 200 with correct user + schema."""
        r = get("/profile")
        assert r.status_code == 200
        data = r.json()
        assert data.get("user_id") == 2
        for key in ("user_id", "name", "email", "phone"):
            assert key in data, f"Missing key '{key}' in profile"

    def test_P02_update_profile_valid(self):
        """P-02: PUT /profile with valid name + phone → 200."""
        r = put("/profile", {"name": "Kate Wilson", "phone": "9704513903"})
        assert r.status_code == 200

    def test_P03_name_too_short_returns_400(self):
        """P-03: name with 1 char → 400."""
        r = put("/profile", {"name": "K", "phone": "9704513903"})
        assert r.status_code == 400

    def test_P04_name_too_long_returns_400(self):
        """P-04: name with 51 chars → 400."""
        r = put("/profile", {"name": "K" * 51, "phone": "9704513903"})
        assert r.status_code == 400

    def test_P05_name_boundary_min_2_chars(self):
        """P-05: name with exactly 2 chars → 200."""
        r = put("/profile", {"name": "KW", "phone": "9704513903"})
        assert r.status_code == 200

    def test_P06_name_boundary_max_50_chars(self):
        """P-06: name with exactly 50 chars → 200."""
        r = put("/profile", {"name": "K" * 50, "phone": "9704513903"})
        assert r.status_code == 200

    def test_P07_phone_too_short_returns_400(self):
        """P-07: phone with 3 digits → 400."""
        r = put("/profile", {"name": "Kate Wilson", "phone": "123"})
        assert r.status_code == 400

    def test_P08_phone_with_letters_returns_400(self):
        """P-08: phone containing letters → 400."""
        r = put("/profile", {"name": "Kate Wilson", "phone": "97045abc03"})
        assert r.status_code == 400

    def test_P09_phone_11_digits_returns_400(self):
        """P-09: phone with 11 digits → 400."""
        r = put("/profile", {"name": "Kate Wilson", "phone": "97045139030"})
        assert r.status_code == 400
