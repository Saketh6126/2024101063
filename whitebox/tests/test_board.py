import pytest
from moneypoly.board import Board
from moneypoly.player import Player

def test_board_initialization():
    board = Board()
    assert len(board.properties) > 0
    assert len(board.groups) > 0
    # Test property groups populated correctly
    assert board.properties[0].name == "Mediterranean Avenue"
    assert board.get_tile_type(0) == "go"

def test_get_tile_type():
    board = Board()
    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(2) == "community_chest"
    assert board.get_tile_type(4) == "income_tax"
    assert board.get_tile_type(5) == "railroad"
    assert board.get_tile_type(7) == "chance"
    assert board.get_tile_type(10) == "jail"
    assert board.get_tile_type(20) == "free_parking"
    assert board.get_tile_type(30) == "go_to_jail"
    assert board.get_tile_type(38) == "luxury_tax"
    
    # Test fallback
    assert board.get_tile_type(999) == "blank"

def test_get_property_at():
    board = Board()
    prop = board.get_property_at(1)
    assert prop is not None
    assert prop.name == "Mediterranean Avenue"
    
    # Not a property
    assert board.get_property_at(0) is None
    # Out of bounds/unknown
    assert board.get_property_at(999) is None

def test_is_purchasable():
    board = Board()
    player = Player("Alice")
    
    # Available property
    assert board.is_purchasable(1) is True
    
    # Non-property
    assert board.is_purchasable(0) is False
    
    # Owned property
    prop = board.get_property_at(1)
    prop.owner = player
    assert board.is_purchasable(1) is False
    
    # Mortgaged but unowned (technically shouldn't happen naturally, but testing branch)
    prop.owner = None
    prop.mortgage()
    assert board.is_purchasable(1) is False

def test_is_special_tile():
    board = Board()
    assert board.is_special_tile(0) is True     # go
    assert board.is_special_tile(1) is False    # property
    assert board.is_special_tile(2) is True     # community_chest
    assert board.is_special_tile(5) is True     # railroad operates like property in ownership, but might be marked special?
    # Actually wait! In board.py:
    # return self.get_tile_type(position) != "property"
    assert board.is_special_tile(5) is True     # railroad != property string in this context
    assert board.is_special_tile(999) is False   # blank is not in SPECIAL_TILES

def test_ownership_queries():
    board = Board()
    player1 = Player("Alice")
    
    unowned_start = len(board.unowned_properties())
    owned_start = len(board.properties_owned_by(player1))
    
    prop = board.properties[0]
    prop.owner = player1
    
    assert len(board.unowned_properties()) == unowned_start - 1
    assert len(board.properties_owned_by(player1)) == owned_start + 1

def test_board_repr():
    board = Board()
    rep = repr(board)
    assert "Board" in rep
    assert "properties" in rep
    assert "owned" in rep
