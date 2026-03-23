import pytest
from moneypoly.cards import CardDeck

def test_card_deck_initialization():
    cards = [{"id": 1}, {"id": 2}]
    deck = CardDeck(cards)
    assert len(deck) == 2
    assert deck.cards_remaining() == 2

def test_card_deck_draw_and_peek():
    cards = [{"id": 1}, {"id": 2}]
    deck = CardDeck(cards)
    
    # Peek shouldn't advance index
    assert deck.peek() == {"id": 1}
    assert deck.index == 0
    
    # Draw should
    assert deck.draw() == {"id": 1}
    assert deck.index == 1
    assert deck.cards_remaining() == 1
    
    assert deck.draw() == {"id": 2}
    assert deck.index == 2
    
    # Cycles back
    assert deck.draw() == {"id": 1}
    assert deck.index == 3

def test_card_deck_empty():
    deck = CardDeck([])
    assert deck.draw() is None
    assert deck.peek() is None

def test_card_deck_reshuffle():
    cards = [{"id": i} for i in range(10)]
    deck = CardDeck(cards)
    deck.draw()
    deck.reshuffle()
    assert deck.index == 0
    assert len(deck.cards) == 10

def test_card_deck_repr():
    deck = CardDeck([1, 2])
    assert "CardDeck(2 cards, next=0)" in repr(deck)
