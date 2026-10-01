from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str, Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass
class Order:
    product_id: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Decimal | None = None

    order_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Decimal | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self):
        self.side = OrderSide(self.side)
        self.order_type = OrderType(self.order_type)
        self.quantity = Decimal(str(self.quantity))

        if self.price is not None:
            self.price = Decimal(str(self.price))

        if self.quantity <= 0:
            raise ValueError("Order quantity must be greater than zero.")

        if self.order_type == OrderType.LIMIT:
            if self.price is None or self.price <= 0:
                raise ValueError(
                    "Limit orders require a positive price."
                )

    @property
    def remaining_quantity(self):
        return self.quantity - self.filled_quantity

    def record_fill(self, quantity, price):
        quantity = Decimal(str(quantity))
        price = Decimal(str(price))

        if quantity <= 0:
            raise ValueError("Fill quantity must be greater than zero.")

        if quantity > self.remaining_quantity:
            raise ValueError(
                "Fill quantity exceeds remaining order quantity."
            )

        previous_value = (
            self.filled_quantity
            * (self.average_fill_price or Decimal("0"))
        )

        new_value = quantity * price
        self.filled_quantity += quantity

        self.average_fill_price = (
            previous_value + new_value
        ) / self.filled_quantity

        if self.remaining_quantity == 0:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED

    def cancel(self):
        if self.status == OrderStatus.FILLED:
            raise ValueError("A filled order cannot be cancelled.")

        self.status = OrderStatus.CANCELLED