from decimal import Decimal

from src.orders import OrderSide
from src.positions import Portfolio


class RiskLimitExceeded(ValueError):
    pass


class RiskManager:
    def __init__(
        self,
        max_order_quantity,
        max_position_quantity,
        max_order_notional,
        max_realized_loss,
    ):
        self.max_order_quantity = Decimal(
            str(max_order_quantity)
        )
        self.max_position_quantity = Decimal(
            str(max_position_quantity)
        )
        self.max_order_notional = Decimal(
            str(max_order_notional)
        )
        self.max_realized_loss = Decimal(
            str(max_realized_loss)
        )

    def validate_order(
        self,
        order,
        portfolio: Portfolio,
        market_price,
    ):
        market_price = Decimal(str(market_price))

        if market_price <= 0:
            raise ValueError(
                "Market price must be greater than zero."
            )

        if order.quantity > self.max_order_quantity:
            raise RiskLimitExceeded(
                "Order quantity exceeds the allowed limit."
            )

        order_notional = order.quantity * market_price

        if order_notional > self.max_order_notional:
            raise RiskLimitExceeded(
                "Order notional exceeds the allowed limit."
            )

        position = portfolio.get_position(
            order.product_id
        )

        signed_quantity = (
            order.quantity
            if order.side == OrderSide.BUY
            else -order.quantity
        )

        projected_position = (
            position.quantity + signed_quantity
        )

        if (
            abs(projected_position)
            > self.max_position_quantity
        ):
            raise RiskLimitExceeded(
                "Projected position exceeds the allowed limit."
            )

        if (
            portfolio.total_realized_pnl()
            <= -self.max_realized_loss
        ):
            raise RiskLimitExceeded(
                "Maximum realized-loss limit has been reached."
            )

        return True