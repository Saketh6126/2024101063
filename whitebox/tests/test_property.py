import pytest
from moneypoly.property import Property, PropertyGroup
from moneypoly.player import Player

def test_property_initialization():
    prop = Property("Boardwalk", 39, 400, 50)
    assert prop.name == "Boardwalk"
    assert prop.position == 39
    assert prop.price == 400
    assert prop.base_rent == 50
    assert prop.owner is None
    assert not prop.is_mortgaged
    assert prop.houses == 0
    assert prop.group is None

def test_property_mortgage_value():
    prop = Property("Baltic Avenue", 3, 60, 4)
    assert prop.mortgage_value == 30

def test_property_mortgage():
    prop = Property("Baltic Avenue", 3, 60, 4)
    # Mortgage it
    payout = prop.mortgage()
    assert payout == 30
    assert prop.is_mortgaged is True
    
    # Mortgage again should return 0
    payout_again = prop.mortgage()
    assert payout_again == 0

def test_property_unmortgage():
    prop = Property("Baltic Avenue", 3, 60, 4)
    prop.mortgage()
    
    # Unmortgage
    cost = prop.unmortgage()
    assert cost == int(30 * 1.1)
    assert prop.is_mortgaged is False
    
    # Unmortgage again should return 0
    cost_again = prop.unmortgage()
    assert cost_again == 0

def test_property_is_available():
    prop = Property("Orient", 6, 100, 6)
    assert prop.is_available() is True
    
    player = Player("Alice")
    prop.owner = player
    assert prop.is_available() is False
    
    prop.owner = None
    prop.is_mortgaged = True
    assert prop.is_available() is False

def test_property_repr():
    prop = Property("Orient", 6, 100, 6)
    assert "unowned" in repr(prop)
    
    player = Player("Alice")
    prop.owner = player
    assert "Alice" in repr(prop)

def test_property_get_rent_basic():
    prop = Property("Orient", 6, 100, 6)
    assert prop.get_rent() == 6
    
    prop.mortgage()
    assert prop.get_rent() == 0

def test_property_get_rent_full_group():
    player = Player("Alice")
    group = PropertyGroup("Light Blue", "lightblue")
    p1 = Property("Oriental", 6, 100, 6)
    p2 = Property("Vermont", 8, 100, 6)
    
    group.add_property(p1)
    group.add_property(p2)
    
    p1.owner = player
    p2.owner = player
    
    assert p1.get_rent() == 12  # Double rent
    
    p2.owner = None
    assert p1.get_rent() == 6   # Drops back to base rent

def test_property_group_basic():
    group = PropertyGroup("Green", "green")
    assert group.size() == 0
    
    p1 = Property("Pacific", 31, 300, 26)
    group.add_property(p1)
    assert group.size() == 1
    assert p1.group == group
    
    group.add_property(p1) # add duplicate
    assert group.size() == 1

def test_property_group_all_owned_by():
    player = Player("Alice")
    other = Player("Bob")
    group = PropertyGroup("Brown", "brown")
    p1 = Property("Baltic", 3, 60, 4)
    p2 = Property("Mediter", 1, 60, 2)
    
    group.add_property(p1)
    group.add_property(p2)
    
    assert group.all_owned_by(player) is False
    assert group.all_owned_by(None) is False
    
    p1.owner = player
    assert group.all_owned_by(player) is False
    
    p2.owner = player
    assert group.all_owned_by(player) is True
    
    p2.owner = other
    assert group.all_owned_by(player) is False

def test_property_group_owner_counts():
    player1 = Player("Alice")
    player2 = Player("Bob")
    group = PropertyGroup("Yellow", "yellow")
    p1 = Property("Atlantic", 26, 260, 22)
    p2 = Property("Ventnor", 27, 260, 22)
    p3 = Property("Marvin", 29, 280, 24)
    
    group.add_property(p1)
    group.add_property(p2)
    group.add_property(p3)
    
    p1.owner = player1
    p2.owner = player1
    p3.owner = player2
    
    counts = group.get_owner_counts()
    assert counts[player1] == 2
    assert counts[player2] == 1
    
    assert "Yellow" in repr(group)
    assert "3 properties" in repr(group)
