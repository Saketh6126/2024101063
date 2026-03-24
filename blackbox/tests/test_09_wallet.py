"""
test_09_wallet.py
-----------------
W-01 to W-09: Wallet balance, top-up, and payment tests.
"""

from conftest import get, post


class TestWallet:

    def test_W01_get_wallet_schema(self):
        """W-01: GET /wallet → 200 with balance field."""
        r = get("/wallet")
        assert r.status_code == 200
        data = r.json()
        has_balance = "wallet_balance" in data or "balance" in data
        assert has_balance, f"No balance key found in wallet response: {list(data.keys())}"

    def test_W02_add_valid_amount(self):
        """W-02: Add amount=100 → 200/201."""
        r = post("/wallet/add", {"amount": 100})
        assert r.status_code in (200, 201)

    def test_W03_add_zero_returns_400(self):
        """W-03: amount=0 → 400 (must be > 0)."""
        r = post("/wallet/add", {"amount": 0})
        assert r.status_code == 400

    def test_W04_add_above_100000_returns_400(self):
        """W-04: amount=100001 → 400 (exceeds max of 100000)."""
        r = post("/wallet/add", {"amount": 100001})
        assert r.status_code == 400

    def test_W05_add_exactly_100000_accepted(self):
        """W-05: amount=100000 → 200 (boundary: max accepted)."""
        r = post("/wallet/add", {"amount": 100000})
        assert r.status_code in (200, 201)

    def test_W06_pay_valid_amount(self):
        """W-06: Pay amount=50 → 200."""
        post("/wallet/add", {"amount": 500})
        r = post("/wallet/pay", {"amount": 50})
        assert r.status_code == 200

    def test_W07_pay_zero_returns_400(self):
        """W-07: Pay amount=0 → 400."""
        r = post("/wallet/pay", {"amount": 0})
        assert r.status_code == 400

    def test_W08_pay_insufficient_balance_returns_400(self):
        """W-08: Pay more than balance → 400."""
        wallet = get("/wallet").json()
        balance = wallet.get("wallet_balance") or wallet.get("balance", 0)
        r = post("/wallet/pay", {"amount": balance + 999999})
        assert r.status_code == 400

    def test_W09_pay_deducts_exact_amount(self):
        """W-09: balance_after = balance_before - 50 (exact deduction)."""
        post("/wallet/add", {"amount": 500})
        before = get("/wallet").json()
        bal_before = before.get("wallet_balance") or before.get("balance", 0)
        post("/wallet/pay", {"amount": 50})
        after = get("/wallet").json()
        bal_after = after.get("wallet_balance") or after.get("balance", 0)
        assert abs((bal_before - 50) - bal_after) < 0.01, \
            f"Wrong deduction: before={bal_before}, after={bal_after}, expected diff=50"
