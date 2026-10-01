from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.order_book import OrderBook
from src.orders import Order, OrderSide, OrderType


@dataclass
class Execution:
    order_id: str
    product_id: str
    side: OrderSide
    quantity: Decimal
    price: Decimal

    execution_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ExecutionEngine:
    def execute_market_order(
        self,
        order: Order,
        order_book: OrderBook,
    ):
        if order.order_type != OrderType.MARKET:
            raise ValueError(
                "This method only executes market orders."
            )

        if order.product_id != order_book.product_id:
            raise ValueError(
                "Order and order book products do not match."
            )

        if order.side == OrderSide.BUY:
            levels = sorted(order_book.asks.items())
            book_side = "sell"
        else:
            levels = sorted(
                order_book.bids.items(),
                reverse=True,
            )
            book_side = "buy"

        executions = []

        for price, available_size in levels:
            if order.remaining_quantity == 0:
                break

            fill_quantity = min(
                order.remaining_quantity,
                available_size,
            )

            order.record_fill(fill_quantity, price)

            executions.append(
                Execution(
                    order_id=order.order_id,
                    product_id=order.product_id,
                    side=order.side,
                    quantity=fill_quantity,
                    price=price,
                )
            )

            remaining_level_size = (
                available_size - fill_quantity
            )

            order_book.update(
                book_side,
                price,
                remaining_level_size,
            )

        return executions