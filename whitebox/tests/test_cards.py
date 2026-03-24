import pytest
from unittest.mock import patch
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
    
    # After exhausting the deck, it should reshuffle before the next draw.
    # Mock shuffle so the behavior is deterministic.
    def reverse_in_place(items):
        items.reverse()

    with patch("moneypoly.cards.random.shuffle", side_effect=reverse_in_place) as shuf:
        assert deck.draw() == {"id": 2}
        shuf.assert_called_once()
        assert deck.index == 1

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
