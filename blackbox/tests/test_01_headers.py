"""
test_01_headers.py
------------------
H-01 to H-07: Global header validation tests.
Headers enforced by middleware — testing on representative endpoints covers all.
"""

import requests
from conftest import BASE, ROLL, HEADERS, USER_HEADERS


class TestHeaderValidation:

    def test_H01_missing_roll_admin_returns_401(self):
        """H-01: No headers on admin endpoint → 401."""
        r = requests.get(BASE + "/admin/users")
        assert r.status_code == 401

    def test_H02_missing_roll_user_endpoint_returns_401(self):
        """H-02: No headers on user endpoint → 401."""
        r = requests.get(BASE + "/profile")
        assert r.status_code == 401

    def test_H03_non_integer_roll_number_returns_400(self):
        """H-03: X-Roll-Number with letters → 400."""
        r = requests.get(BASE + "/admin/users", headers={"X-Roll-Number": "abc"})
        assert r.status_code == 400

    def test_H04_missing_user_id_on_user_endpoint_returns_400(self):
        """H-04: User-scoped endpoint with only X-Roll-Number → 400."""
        r = requests.get(BASE + "/profile", headers=HEADERS)
        assert r.status_code == 400

    def test_H05_non_integer_user_id_returns_400(self):
        """H-05: X-User-ID with letters → 400."""
        r = requests.get(BASE + "/profile",
                         headers={"X-Roll-Number": ROLL, "X-User-ID": "abc"})
        assert r.status_code == 400

    def test_H06_nonexistent_user_id_returns_400(self):
        """H-06: X-User-ID pointing to non-existent user → 400."""
        r = requests.get(BASE + "/profile",
                         headers={"X-Roll-Number": ROLL, "X-User-ID": "999999"})
        assert r.status_code == 400

    def test_H07_admin_works_without_user_id(self):
        """H-07: Admin endpoint works with only X-Roll-Number → 200."""
        r = requests.get(BASE + "/admin/users", headers=HEADERS)
        assert r.status_code == 200
