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

def test_load_snapshot():
    book = OrderBook("BTC-USD")

    bids = [
        ["100.00", "2.0"],
        ["99.00", "3.0"],
    ]

    asks = [
        ["101.00", "1.5"],
        ["102.00", "4.0"],
    ]

    book.load_snapshot(bids, asks)

    assert book.best_bid() == Decimal("100.00")
    assert book.best_ask() == Decimal("101.00")
    assert book.spread() == Decimal("1.00")


def test_snapshot_replaces_existing_book():
    book = OrderBook("BTC-USD")

    book.update("buy", "90.00", "5.0")
    book.update("sell", "110.00", "5.0")

    book.load_snapshot(
        bids=[["100.00", "2.0"]],
        asks=[["101.00", "3.0"]],
    )

    assert Decimal("90.00") not in book.bids
    assert Decimal("110.00") not in book.asks
    assert book.best_bid() == Decimal("100.00")
    assert book.best_ask() == Decimal("101.00")


def test_live_updates_after_snapshot():
    book = OrderBook("BTC-USD")

    book.load_snapshot(
        bids=[["100.00", "2.0"]],
        asks=[["101.00", "3.0"]],
    )

    book.update("buy", "100.50", "1.25")
    book.update("sell", "101.00", "0")
    book.update("sell", "101.50", "2.5")

    assert book.best_bid() == Decimal("100.50")
    assert book.best_ask() == Decimal("101.50")
    assert book.spread() == Decimal("1.00")