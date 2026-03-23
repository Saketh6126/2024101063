import pytest
from moneypoly.player import Player
from moneypoly.config import STARTING_BALANCE, BOARD_SIZE, GO_SALARY, JAIL_POSITION

class MockProperty:
    def __init__(self, name="Mock Prop"):
        self.name = name

def test_player_initialization():
    player = Player("Alice")
    assert player.name == "Alice"
    assert player.balance == STARTING_BALANCE
    assert player.position == 0
    assert len(player.properties) == 0
    assert not player.in_jail
    assert player.jail_turns == 0
    assert player.get_out_of_jail_cards == 0
    assert not player.is_eliminated

def test_player_initialization_custom_balance():
    player = Player("Bob", balance=500)
    assert player.balance == 500

def test_add_money():
    player = Player("Alice", balance=100)
    player.add_money(50)
    assert player.balance == 150

def test_add_money_negative_raises_valueerror():
    player = Player("Alice", balance=100)
    with pytest.raises(ValueError, match="Cannot add a negative amount"):
        player.add_money(-50)

def test_deduct_money():
    player = Player("Alice", balance=100)
    player.deduct_money(50)
    assert player.balance == 50

def test_deduct_money_negative_raises_valueerror():
    player = Player("Alice", balance=100)
    with pytest.raises(ValueError, match="Cannot deduct a negative amount"):
        player.deduct_money(-50)

def test_is_bankrupt():
    player = Player("Alice", balance=1)
    assert not player.is_bankrupt()
    player.deduct_money(1)
    assert player.is_bankrupt()
    player.deduct_money(50)
    assert player.is_bankrupt()

def test_net_worth():
    player = Player("Alice", balance=350)
    assert player.net_worth() == 350

def test_move_no_wrap():
    player = Player("Alice", balance=100)
    player.position = 5
    pos = player.move(10)
    assert pos == 15
    assert player.position == 15
    assert player.balance == 100  # No Go salary

def test_move_with_wrap(capsys):
    player = Player("Alice", balance=100)
    player.position = BOARD_SIZE - 2
    pos = player.move(2)
    assert pos == 0
    assert player.position == 0
    assert player.balance == 100 + GO_SALARY
    
    captured = capsys.readouterr()
    assert "landed on or passed Go and collected" in captured.out

def test_move_past_go(capsys):
    player = Player("Alice", balance=100)
    player.position = BOARD_SIZE - 2
    pos = player.move(5)
    assert pos == 3
    assert player.position == 3
    assert player.balance == 100 + GO_SALARY
    
    captured = capsys.readouterr()
    assert "landed on or passed Go and collected" in captured.out

def test_go_to_jail():
    player = Player("Alice")
    player.position = 5
    player.go_to_jail()
    assert player.position == JAIL_POSITION
    assert player.in_jail
    assert player.jail_turns == 0

def test_add_and_remove_property():
    player = Player("Alice")
    prop1 = MockProperty("Prop1")
    prop2 = MockProperty("Prop2")
    
    player.add_property(prop1)
    player.add_property(prop2)
    assert player.count_properties() == 2
    
    # Do not add duplicate
    player.add_property(prop1)
    assert player.count_properties() == 2

    # Remove existing
    player.remove_property(prop1)
    assert player.count_properties() == 1
    assert prop1 not in player.properties
    
    # Remove non-existing
    player.remove_property(prop1)
    assert player.count_properties() == 1

def test_status_line():
    player = Player("Alice", balance=200)
    player.position = 5
    line = player.status_line()
    assert "Alice: $200" in line
    assert "pos=5" in line
    assert "props=0" in line
    assert "[JAILED]" not in line
    
    player.in_jail = True
    line_jailed = player.status_line()
    assert "[JAILED]" in line_jailed

def test_repr():
    player = Player("Alice", balance=200)
    player.position = 5
    rep = repr(player)
    assert "Player('Alice'" in rep
    assert "balance=200" in rep
    assert "pos=5" in rep

def test_state_properties():
    player = Player("Alice")
    player.in_jail = True
    assert player.in_jail is True
    
    player.jail_turns = 2
    assert player.jail_turns == 2
    
    player.get_out_of_jail_cards = 1
    assert player.get_out_of_jail_cards == 1
    
    player.is_eliminated = True
    assert player.is_eliminated is True
