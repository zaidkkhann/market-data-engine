from dataclasses import dataclass
from decimal import Decimal

from src.execution_engine import Execution
from src.orders import OrderSide


@dataclass
class Position:
    product_id: str
    quantity: Decimal = Decimal("0")
    average_entry_price: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")

    def apply_execution(self, execution: Execution):
        execution_quantity = Decimal(str(execution.quantity))
        execution_price = Decimal(str(execution.price))

        signed_quantity = (
            execution_quantity
            if execution.side == OrderSide.BUY
            else -execution_quantity
        )

        same_direction = (
            self.quantity == 0
            or (
                self.quantity > 0
                and signed_quantity > 0
            )
            or (
                self.quantity < 0
                and signed_quantity < 0
            )
        )

        if same_direction:
            current_value = (
                abs(self.quantity)
                * self.average_entry_price
            )

            new_value = (
                execution_quantity
                * execution_price
            )

            self.quantity += signed_quantity

            self.average_entry_price = (
                current_value + new_value
            ) / abs(self.quantity)

            return

        closing_quantity = min(
            abs(self.quantity),
            execution_quantity,
        )

        if self.quantity > 0:
            self.realized_pnl += closing_quantity * (
                execution_price
                - self.average_entry_price
            )
        else:
            self.realized_pnl += closing_quantity * (
                self.average_entry_price
                - execution_price
            )

        previous_quantity = self.quantity
        self.quantity += signed_quantity

        if self.quantity == 0:
            self.average_entry_price = Decimal("0")

        elif (
            previous_quantity > 0
            and self.quantity < 0
        ) or (
            previous_quantity < 0
            and self.quantity > 0
        ):
            self.average_entry_price = execution_price

    def unrealized_pnl(self, market_price):
        market_price = Decimal(str(market_price))

        if self.quantity > 0:
            return self.quantity * (
                market_price
                - self.average_entry_price
            )

        if self.quantity < 0:
            return abs(self.quantity) * (
                self.average_entry_price
                - market_price
            )

        return Decimal("0")

    def market_value(self, market_price):
        market_price = Decimal(str(market_price))
        return self.quantity * market_price


class Portfolio:
    def __init__(self):
        self.positions = {}

    def apply_execution(self, execution):
        if execution.product_id not in self.positions:
            self.positions[execution.product_id] = Position(
                product_id=execution.product_id
            )

        position = self.positions[execution.product_id]
        position.apply_execution(execution)

        return position

    def get_position(self, product_id):
        return self.positions.get(
            product_id,
            Position(product_id=product_id),
        )

    def total_realized_pnl(self):
        return sum(
            (
                position.realized_pnl
                for position in self.positions.values()
            ),
            Decimal("0"),
        )