import pytest
from moneypoly.bank import Bank
from moneypoly.player import Player
from moneypoly.config import BANK_STARTING_FUNDS

def test_bank_initialization():
    b = Bank()
    assert b.get_balance() == BANK_STARTING_FUNDS
    assert b.total_loans_issued() == 0
    assert b.loan_count() == 0

def test_bank_collect():
    b = Bank()
    b.collect(500)
    assert b.get_balance() == BANK_STARTING_FUNDS + 500

def test_bank_pay_out():
    b = Bank()
    res = b.pay_out(100)
    assert res == 100
    assert b.get_balance() == BANK_STARTING_FUNDS - 100

def test_bank_pay_out_negative_or_zero():
    b = Bank()
    assert b.pay_out(0) == 0
    assert b.pay_out(-50) == 0
    assert b.get_balance() == BANK_STARTING_FUNDS

def test_bank_pay_out_insufficient_funds():
    b = Bank()
    with pytest.raises(ValueError, match="Bank cannot pay"):
        b.pay_out(BANK_STARTING_FUNDS + 1)

def test_bank_give_loan(capsys):
    b = Bank()
    p = Player("Alice", balance=0)
    b.give_loan(p, 200)
    assert p.balance == 200
    assert b.loan_count() == 1
    assert b.total_loans_issued() == 200
    assert "emergency loan" in capsys.readouterr().out

def test_bank_give_loan_negative_or_zero():
    b = Bank()
    p = Player("Alice", balance=0)
    b.give_loan(p, 0)
    b.give_loan(p, -50)
    assert p.balance == 0
    assert b.loan_count() == 0

def test_bank_summary_and_repr(capsys):
    b = Bank()
    b.give_loan(Player("Alice"), 500)
    b.summary()
    out = capsys.readouterr().out
    assert "Bank reserves" in out
    assert "Total collected:" in out
    assert "Loans issued" in out
    
    assert "Bank(funds=" in repr(b)
