import pytest
from unittest.mock import patch, MagicMock
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property
from moneypoly.config import STARTING_BALANCE
import sys

def test_game_initialization():
    g = Game(["Alice", "Bob"])
    assert len(g.players) == 2
    assert g.players[0].name == "Alice"
    assert g.current_index == 0
    assert g.turn_number == 0
    assert g.running is True

def test_advance_turn():
    g = Game(["Alice", "Bob", "Charlie"])
    assert g.current_player().name == "Alice"
    g.advance_turn()
    assert g.current_player().name == "Bob"
    g.advance_turn()
    assert g.current_player().name == "Charlie"
    g.advance_turn()
    assert g.current_player().name == "Alice"
    assert g.turn_number == 3

def test_find_winner():
    g = Game(["Alice", "Bob"])
    g.players[0].balance = 100
    g.players[1].balance = 500
    
    # Bug: this currently returns min() instead of max()!
    winner = g.find_winner()
    assert winner.name == "Bob"

def test_play_turn_jail(capsys):
    g = Game(["Alice", "Bob"])
    p = g.current_player()
    p.go_to_jail()
    
    with patch("moneypoly.ui.confirm", return_value=False):
        g.play_turn()
        
    assert p.jail_turns == 1
    assert p.in_jail is True

def test_play_turn_doubles_to_jail(capsys):
    g = Game(["Alice", "Bob"])
    g.dice.is_doubles = MagicMock(return_value=True)
    g.dice.doubles_streak = 3
    
    g.play_turn()
    p = g.players[0]
    assert p.in_jail is True


def test_play_turn_invokes_interactive_menu_in_tty():
    g = Game(["Alice", "Bob"])
    g.dice.roll = MagicMock(return_value=0)
    g.dice.is_doubles = MagicMock(return_value=False)

    with patch.object(sys.stdin, "isatty", return_value=True):
        with patch.object(Game, "interactive_menu") as menu:
            g.play_turn()
            menu.assert_called_once()

@patch("builtins.input", side_effect=["s"]) # skip buying
def test_buy_property_skip(mock_input, capsys):
    g = Game(["Alice", "Bob"])
    p = g.current_player()
    # Mediterranean Ave pos = 1
    g.dice.roll = MagicMock(return_value=1)
    g.dice.is_doubles = MagicMock(return_value=False)
    g.play_turn()
    
    # Should move to 1 and ask to buy
    assert p.position == 1
    assert p.balance == STARTING_BALANCE
    prop = g.board.get_property_at(1)
    assert prop.owner is None

@patch("builtins.input", side_effect=["b"]) # buy
def test_buy_property_buy(mock_input):
    g = Game(["Alice", "Bob"])
    p = g.current_player()
    g.dice.roll = MagicMock(return_value=1)
    g.dice.is_doubles = MagicMock(return_value=False)
    g.play_turn()
    
    prop = g.board.get_property_at(1)
    assert prop.owner == p
    assert p.balance == STARTING_BALANCE - 60

@patch("builtins.input", side_effect=["a", "65", "0"]) # auction
def test_buy_property_auction(mock_input):
    g = Game(["Alice", "Bob"])
    p = g.current_player()
    g.dice.roll = MagicMock(return_value=1)
    g.dice.is_doubles = MagicMock(return_value=False)
    g.play_turn()
    
    prop = g.board.get_property_at(1)
    assert prop.owner == p  # Alice bid 65
    assert p.balance == STARTING_BALANCE - 65

def test_auction_logic():
    g = Game(["Alice", "Bob"])
    prop = g.board.get_property_at(1)
    
    # Alice bids 0, Bob bids 100
    with patch("moneypoly.ui.safe_int_input", side_effect=[0, 100]):
        g.auction_property(prop)
        assert prop.owner.name == "Bob"
        assert g.players[1].balance == STARTING_BALANCE - 100

def test_auction_logic_all_pass():
    g = Game(["Alice", "Bob"])
    prop = g.board.get_property_at(1)
    
    with patch("moneypoly.ui.safe_int_input", side_effect=[0, 0]):
        g.auction_property(prop)
        assert prop.owner is None

def test_pay_rent():
    g = Game(["Alice", "Bob"])
    prop = g.board.get_property_at(1)
    prop.owner = g.players[1] # Bob owns it
    
    # Alice rolls 1
    g.dice.roll = MagicMock(return_value=1)
    g.dice.is_doubles = MagicMock(return_value=False)
    g.play_turn()
    
    assert g.players[0].balance == STARTING_BALANCE - 2
    assert g.players[1].balance == STARTING_BALANCE + 2

def test_mortgage_and_unmortgage_commands():
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    
    # Direct method calls
    res = g.mortgage_property(p, prop)
    assert res is True
    assert prop.is_mortgaged is True
    assert p.balance == STARTING_BALANCE + 30
    
    res2 = g.unmortgage_property(p, prop)
    assert res2 is True
    assert prop.is_mortgaged is False
    assert p.balance == STARTING_BALANCE + 30 - int(30 * 1.1)

def test_trade_logic():
    g = Game(["Alice", "Bob"])
    p1 = g.players[0]
    p2 = g.players[1]
    prop = g.board.get_property_at(1)
    prop.owner = p1
    
    # Alice trades prop to Bob for 500
    res = g.trade(p1, p2, prop, 500)
    assert res is True
    assert prop.owner == p2
    assert p1.balance == STARTING_BALANCE + 500
    assert p2.balance == STARTING_BALANCE - 500

def test_bankruptcy_skips():
    # If Alice goes bankrupt, Bob shouldn't be skipped!
    g = Game(["Alice", "Bob", "Charlie"])
    
    # Alice lands on Luxury Tax (38) intentionally several times?
    # She has $1500. We will bankrupt her manually.
    g.players[0].balance = 10
    
    g.dice.roll = MagicMock(return_value=38) # Luxury tax is 38
    g.dice.is_doubles = MagicMock(return_value=False)
    
    g.play_turn()
    
    # Alice is removed!
    assert len(g.players) == 2
    # If advance_turn is called, current_index becomes 1.
    # Player 1 is Charlie! Bob (at index 0 now) gets skipped.
    assert g.current_player().name == "Bob"

@patch("builtins.input", side_effect=["s"])
def test_apply_card_actions(mock_input):
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    
    card1 = {"action": "collect", "value": 50, "description": ""}
    g._apply_card(p, card1)
    assert p.balance == STARTING_BALANCE + 50
    
    card2 = {"action": "pay", "value": 50, "description": ""}
    g._apply_card(p, card2)
    assert p.balance == STARTING_BALANCE
    
    card3 = {"action": "jail", "value": 0, "description": ""}
    g._apply_card(p, card3)
    assert p.in_jail is True
    
    card4 = {"action": "jail_free", "value": 0, "description": ""}
    g._apply_card(p, card4)
    assert p.get_out_of_jail_cards == 1
    
    # move_to
    p.in_jail = False
    card5 = {"action": "move_to", "value": 39, "description": ""} # Boardwalk
    g._apply_card(p, card5)
    assert p.position == 39
    
    card6 = {"action": "birthday", "value": 10, "description": ""}
    g._apply_card(p, card6)
    assert p.balance == STARTING_BALANCE + 10
    assert g.players[1].balance == STARTING_BALANCE - 10
