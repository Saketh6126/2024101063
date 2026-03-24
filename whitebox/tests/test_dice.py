import pytest
from unittest.mock import patch
from moneypoly.dice import Dice

def test_dice_initialization():
    d = Dice()
    assert d.die1 == 0
    assert d.die2 == 0
    assert d.doubles_streak == 0
    assert d.total() == 0
    assert d.is_doubles() is True # 0 == 0

def test_dice_roll_bounds():
    d = Dice()
    for _ in range(100):
        total = d.roll()
        assert 1 <= d.die1 <= 6
        assert 1 <= d.die2 <= 6
        assert 2 <= total <= 12

@patch("random.randint", side_effect=[3, 3, 2, 4])
def test_dice_doubles_streak(mock_randint):
    d = Dice()
    # First roll: 3, 3
    d.roll()
    assert d.is_doubles() is True
    assert d.doubles_streak == 1
    
    # Second roll: 2, 4
    d.roll()
    assert d.is_doubles() is False
    assert d.doubles_streak == 0

def test_dice_reset():
    d = Dice()
    d.roll()
    d.doubles_streak = 2
    d.reset()
    assert d.die1 == 0
    assert d.die2 == 0
    assert d.doubles_streak == 0

def test_dice_describe():
    d = Dice()
    d.die1 = 3
    d.die2 = 3
    assert "(DOUBLES)" in d.describe()
    assert "3 + 3 = 6" in d.describe()
    
    d.die1 = 2
    d.die2 = 3
    assert "(DOUBLES)" not in d.describe()

def test_dice_repr():
    d = Dice()
    assert "Dice(die1=0, die2=0, streak=0)" in repr(d)
