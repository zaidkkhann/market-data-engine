from decimal import Decimal

from src.execution_engine import Execution
from src.orders import OrderSide
from src.positions import Position


def create_execution(side, quantity, price):
    return Execution(
        order_id="test-order",
        product_id="BTC-USD",
        side=OrderSide(side),
        quantity=Decimal(quantity),
        price=Decimal(price),
    )


def test_long_position_average_price():
    position = Position("BTC-USD")

    position.apply_execution(
        create_execution("buy", "1", "100")
    )
    position.apply_execution(
        create_execution("buy", "1", "110")
    )

    assert position.quantity == Decimal("2")
    assert position.average_entry_price == Decimal("105")


def test_long_position_unrealized_profit():
    position = Position("BTC-USD")

    position.apply_execution(
        create_execution("buy", "2", "100")
    )

    assert position.unrealized_pnl("110") == Decimal("20")


def test_closing_long_position_realizes_profit():
    position = Position("BTC-USD")

    position.apply_execution(
        create_execution("buy", "2", "100")
    )
    position.apply_execution(
        create_execution("sell", "2", "110")
    )

    assert position.quantity == Decimal("0")
    assert position.realized_pnl == Decimal("20")


def test_short_position_profit():
    position = Position("BTC-USD")

    position.apply_execution(
        create_execution("sell", "2", "100")
    )

    assert position.quantity == Decimal("-2")
    assert position.unrealized_pnl("90") == Decimal("20")


def test_position_can_flip_from_long_to_short():
    position = Position("BTC-USD")

    position.apply_execution(
        create_execution("buy", "1", "100")
    )
    position.apply_execution(
        create_execution("sell", "2", "110")
    )

    assert position.quantity == Decimal("-1")
    assert position.average_entry_price == Decimal("110")
    assert position.realized_pnl == Decimal("10")