"""
test_04_addresses.py
--------------------
AD-01 to AD-20: Address CRUD + validation tests.
"""

import pytest
from conftest import get, post, put, delete, HEADERS


def _valid_address(**overrides):
    base = {"label": "HOME", "street": "123 Test Street", "city": "Hyderabad",
            "pincode": "500081", "is_default": False}
    base.update(overrides)
    return base


def _extract_id(r):
    body = r.json()
    addr = body.get("address", body)
    aid = addr.get("address_id")
    if not aid:
        pytest.skip("Could not extract address_id from response")
    return aid


class TestAddresses:

    def test_AD01_get_addresses_schema(self):
        """AD-01: GET /addresses → 200, returns list."""
        r = get("/addresses")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_AD02_create_address_schema(self):
        """AD-02: POST valid address → 200/201 with full schema."""
        r = post("/addresses", _valid_address())
        assert r.status_code in (200, 201)
        body = r.json()
        addr = body.get("address", body)
        for key in ("address_id", "label", "street", "city", "pincode", "is_default"):
            assert key in addr, f"Missing key '{key}' in address response"

    def test_AD03_invalid_label_returns_400(self):
        """AD-03: label='SCHOOL' → 400."""
        r = post("/addresses", _valid_address(label="SCHOOL"))
        assert r.status_code == 400

    def test_AD04_label_office_accepted(self):
        """AD-04: label='OFFICE' → 200/201."""
        r = post("/addresses", _valid_address(label="OFFICE"))
        assert r.status_code in (200, 201)

    def test_AD05_label_other_accepted(self):
        """AD-05: label='OTHER' → 200/201."""
        r = post("/addresses", _valid_address(label="OTHER"))
        assert r.status_code in (200, 201)

    def test_AD06_street_3_chars_returns_400(self):
        """AD-06: street with 3 chars (< 5) → 400."""
        r = post("/addresses", _valid_address(street="Abc"))
        assert r.status_code == 400

    def test_AD07_street_boundary_5_chars_accepted(self):
        """AD-07: street with exactly 5 chars → 200/201."""
        r = post("/addresses", _valid_address(street="Abcde"))
        assert r.status_code in (200, 201)

    def test_AD08_street_boundary_100_chars_accepted(self):
        """AD-08: street with exactly 100 chars → 200/201."""
        r = post("/addresses", _valid_address(street="A" * 100))
        assert r.status_code in (200, 201)

    def test_AD09_street_101_chars_returns_400(self):
        """AD-09: street with 101 chars → 400."""
        r = post("/addresses", _valid_address(street="A" * 101))
        assert r.status_code == 400

    def test_AD10_pincode_4_digits_returns_400(self):
        """AD-10: pincode with 4 digits → 400."""
        r = post("/addresses", _valid_address(pincode="5000"))
        assert r.status_code == 400

    def test_AD11_pincode_boundary_6_digits_accepted(self):
        """AD-11: pincode with exactly 6 digits → 200/201."""
        r = post("/addresses", _valid_address(pincode="500081"))
        assert r.status_code in (200, 201)

    def test_AD12_pincode_7_digits_returns_400(self):
        """AD-12: pincode with 7 digits → 400."""
        r = post("/addresses", _valid_address(pincode="5000811"))
        assert r.status_code == 400

    def test_AD13_city_1_char_returns_400(self):
        """AD-13: city with 1 char → 400."""
        r = post("/addresses", _valid_address(city="A"))
        assert r.status_code == 400

    def test_AD14_city_51_chars_returns_400(self):
        """AD-14: city with 51 chars → 400."""
        r = post("/addresses", _valid_address(city="A" * 51))
        assert r.status_code == 400

    def test_AD15_single_default_address(self):
        """AD-15: Adding one address as default → only that address is default."""
        r = post("/addresses", _valid_address(label="HOME", is_default=True))
        assert r.status_code in (200, 201)
        addresses = get("/addresses").json()
        defaults = [a for a in addresses if a.get("is_default")]
        assert len(defaults) == 1

    def test_AD16_only_one_default_at_a_time(self):
        """AD-16: Adding 2nd default → 1st flips to false."""
        post("/addresses", _valid_address(label="HOME", is_default=True))
        post("/addresses", _valid_address(label="OFFICE", is_default=True))
        addresses = get("/addresses").json()
        defaults = [a for a in addresses if a.get("is_default")]
        assert len(defaults) == 1

    def test_AD17_update_address_shows_new_data(self):
        """AD-17: PUT updates street + is_default; response shows new data."""
        r = post("/addresses", _valid_address(street="Old Street Road"))
        aid = _extract_id(r)
        r2 = put(f"/addresses/{aid}", {"street": "New Updated Lane", "is_default": False})
        assert r2.status_code == 200
        body = r2.json()
        addr = body.get("address", body)
        assert addr.get("street") == "New Updated Lane"

    def test_AD18_put_cannot_change_label_city_pincode(self):
        """AD-18: PUT with label/city/pincode in body — those fields must not change."""
        r = post("/addresses", _valid_address(label="HOME", city="Hyderabad", pincode="500081"))
        aid = _extract_id(r)
        put(f"/addresses/{aid}", {
            "street": "New Road",
            "is_default": False,
            "label": "OFFICE",
            "city": "Mumbai",
            "pincode": "400001"
        })
        addresses = get("/addresses").json()
        addr = next((a for a in addresses if a.get("address_id") == aid), None)
        assert addr is not None
        assert addr["label"] == "HOME"
        assert addr["city"] == "Hyderabad"
        assert addr["pincode"] == "500081"

    def test_AD19_delete_address(self):
        """AD-19: DELETE valid address → 200/204."""
        r = post("/addresses", _valid_address())
        aid = _extract_id(r)
        rd = delete(f"/addresses/{aid}")
        assert rd.status_code in (200, 204)

    def test_AD20_delete_nonexistent_returns_404(self):
        """AD-20: DELETE /addresses/999999 → 404."""
        r = delete("/addresses/999999")
        assert r.status_code == 404
