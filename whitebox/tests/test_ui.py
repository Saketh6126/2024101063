import pytest
from unittest.mock import patch
from moneypoly.ui import (
    print_banner, print_player_card, print_standings, 
    print_board_ownership, format_currency, safe_int_input, confirm
)
from moneypoly.player import Player
from moneypoly.board import Board

def test_print_banner(capsys):
    print_banner("Test")
    out = capsys.readouterr().out
    assert "Test" in out
    assert "=" * 52 in out

def test_print_player_card(capsys):
    p = Player("Alice", balance=100)
    p.in_jail = True
    p.jail_turns = 2
    p.get_out_of_jail_cards = 1
    print_player_card(p)
    out = capsys.readouterr().out
    assert "IN JAIL" in out
    assert "Alice" in out
    assert "100" in out

def test_print_player_card_with_properties(capsys):
    from moneypoly.property import Property
    p = Player("Bob")
    prop = Property("Test Prop", 1, 100, 10)
    prop.owner = p
    prop.is_mortgaged = True
    p.add_property(prop)
    print_player_card(p)
    out = capsys.readouterr().out
    assert "Test Prop" in out
    assert "[MORTGAGED]" in out

def test_print_standings(capsys):
    p1 = Player("Alice", balance=200)
    p2 = Player("Bob", balance=100)
    p2.in_jail = True
    print_standings([p1, p2])
    out = capsys.readouterr().out
    assert "Alice" in out
    assert "Bob" in out
    assert "[JAILED]" in out

def test_print_board_ownership(capsys):
    b = Board()
    p = Player("Alice")
    prop = b.properties[0]
    prop.owner = p
    prop.is_mortgaged = True
    print_board_ownership(b)
    out = capsys.readouterr().out
    assert "Property Register" in out
    assert "*Alice" in out

def test_format_currency():
    assert format_currency(1500) == "$1,500"

@patch("builtins.input", side_effect=["42", "invalid", ""])
def test_safe_int_input(mock_input):
    assert safe_int_input("Prompt: ") == 42
    assert safe_int_input("Prompt: ", default=99) == 99
    assert safe_int_input("Prompt: ", default=0) == 0

@patch("builtins.input", side_effect=["y", "Y", "yes", "n", "", "no"])
def test_confirm(mock_input):
    assert confirm("Q: ") is True
    assert confirm("Q: ") is True
    assert confirm("Q: ") is False # 'yes' != 'y'
    assert confirm("Q: ") is False
    assert confirm("Q: ") is False
    assert confirm("Q: ") is False
