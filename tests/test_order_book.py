from decimal import Decimal

import pytest

from src.order_book import OrderBook


@pytest.fixture
def order_book():
    book = OrderBook("BTC-USD")

    book.update("buy", "100.00", "2.0")
    book.update("buy", "99.00", "3.0")
    book.update("sell", "101.00", "1.5")
    book.update("sell", "102.00", "4.0")

    return book


def test_best_bid(order_book):
    assert order_book.best_bid() == Decimal("100.00")


def test_best_ask(order_book):
    assert order_book.best_ask() == Decimal("101.00")


def test_spread(order_book):
    assert order_book.spread() == Decimal("1.00")


def test_midpoint(order_book):
    assert order_book.midpoint() == Decimal("100.50")


def test_existing_level_is_updated(order_book):
    order_book.update("buy", "100.00", "7.5")

    assert order_book.bids[Decimal("100.00")] == Decimal("7.5")


def test_zero_size_removes_level(order_book):
    order_book.update("buy", "100.00", "0")

    assert Decimal("100.00") not in order_book.bids
    assert order_book.best_bid() == Decimal("99.00")


def test_top_levels_are_sorted(order_book):
    levels = order_book.get_top_levels(depth=2)

    assert levels["bids"] == [
        (Decimal("100.00"), Decimal("2.0")),
        (Decimal("99.00"), Decimal("3.0")),
    ]

    assert levels["asks"] == [
        (Decimal("101.00"), Decimal("1.5")),
        (Decimal("102.00"), Decimal("4.0")),
    ]


def test_empty_book_returns_none():
    book = OrderBook("BTC-USD")

    assert book.best_bid() is None
    assert book.best_ask() is None
    assert book.spread() is None
    assert book.midpoint() is None


def test_invalid_side_raises_error(order_book):
    with pytest.raises(ValueError):
        order_book.update("invalid", "100.00", "1.0")