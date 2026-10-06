from decimal import Decimal

import pytest

from src.orders import Order
from src.positions import Portfolio, Position
from src.risk import (
    RiskLimitExceeded,
    RiskManager,
)


@pytest.fixture
def risk_manager():
    return RiskManager(
        max_order_quantity="2",
        max_position_quantity="5",
        max_order_notional="1000",
        max_realized_loss="100",
    )


def test_accepts_order_within_limits(risk_manager):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "1",
    )

    assert risk_manager.validate_order(
        order,
        Portfolio(),
        market_price="500",
    )


def test_rejects_excessive_order_quantity(
    risk_manager,
):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "3",
    )

    with pytest.raises(RiskLimitExceeded):
        risk_manager.validate_order(
            order,
            Portfolio(),
            market_price="100",
        )


def test_rejects_excessive_notional(
    risk_manager,
):
    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "2",
    )

    with pytest.raises(RiskLimitExceeded):
        risk_manager.validate_order(
            order,
            Portfolio(),
            market_price="600",
        )


def test_rejects_excessive_projected_position(
    risk_manager,
):
    portfolio = Portfolio()

    portfolio.positions["BTC-USD"] = Position(
        product_id="BTC-USD",
        quantity=Decimal("4"),
        average_entry_price=Decimal("100"),
    )

    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "2",
    )

    with pytest.raises(RiskLimitExceeded):
        risk_manager.validate_order(
            order,
            portfolio,
            market_price="100",
        )


def test_allows_order_that_reduces_position(
    risk_manager,
):
    portfolio = Portfolio()

    portfolio.positions["BTC-USD"] = Position(
        product_id="BTC-USD",
        quantity=Decimal("4"),
        average_entry_price=Decimal("100"),
    )

    order = Order(
        "BTC-USD",
        "sell",
        "market",
        "2",
    )

    assert risk_manager.validate_order(
        order,
        portfolio,
        market_price="100",
    )


def test_rejects_orders_after_loss_limit(
    risk_manager,
):
    portfolio = Portfolio()

    portfolio.positions["BTC-USD"] = Position(
        product_id="BTC-USD",
        realized_pnl=Decimal("-100"),
    )

    order = Order(
        "BTC-USD",
        "buy",
        "market",
        "1",
    )

    with pytest.raises(RiskLimitExceeded):
        risk_manager.validate_order(
            order,
            portfolio,
            market_price="100",
        )
