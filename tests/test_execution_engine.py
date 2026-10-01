from decimal import Decimal

import pytest

from src.execution_engine import ExecutionEngine
from src.order_book import OrderBook
from src.orders import (
    Order,
    OrderStatus,
)


@pytest.fixture
def order_book():
    book = OrderBook("BTC-USD")

    book.update("buy", "99.00", "2.0")
    book.update("buy", "98.00", "3.0")
    book.update("sell", "100.00", "0.5")
    book.update("sell", "101.00", "1.5")

    return book


def test_market_buy_fills_across_ask_levels(order_book):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "1.0",
    )

    executions = ExecutionEngine().execute_market_order(
        order,
        order_book,
    )

    assert order.status == OrderStatus.FILLED
    assert order.filled_quantity == Decimal("1.0")
    assert order.average_fill_price == Decimal("100.5")
    assert len(executions) == 2


def test_market_sell_uses_highest_bids_first(order_book):
    order = Order(
        "BTC-USD",
        "sell",
        "market",
        "3.0",
    )

    executions = ExecutionEngine().execute_market_order(
        order,
        order_book,
    )

    assert order.status == OrderStatus.FILLED
    assert executions[0].price == Decimal("99.00")
    assert executions[1].price == Decimal("98.00")


def test_insufficient_liquidity_causes_partial_fill(order_book):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "5.0",
    )

    ExecutionEngine().execute_market_order(
        order,
        order_book,
    )

    assert order.status == OrderStatus.PARTIALLY_FILLED
    assert order.filled_quantity == Decimal("2.0")
    assert order.remaining_quantity == Decimal("3.0")


def test_execution_reduces_book_liquidity(order_book):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "0.25",
    )

    ExecutionEngine().execute_market_order(
        order,
        order_book,
    )

    assert order_book.asks[Decimal("100.00")] == Decimal("0.25")


def test_fully_consumed_level_is_removed(order_book):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "0.5",
    )

    ExecutionEngine().execute_market_order(
        order,
        order_book,
    )

    assert Decimal("100.00") not in order_book.asks
    assert order_book.best_ask() == Decimal("101.00")


def test_rejects_wrong_product(order_book):
    order = Order(
        "ETH-USD",
        "buy",
        "market",
        "1.0",
    )

    with pytest.raises(ValueError):
        ExecutionEngine().execute_market_order(
            order,
            order_book,
        )


def test_rejects_invalid_quantity():
    with pytest.raises(ValueError):
        Order(
            "BTC-USD",
            "buy",
            "market",
            "0",
        )


def test_limit_order_requires_price():
    with pytest.raises(ValueError):
        Order(
            "BTC-USD",
            "buy",
            "limit",
            "1.0",
        )