from copy import deepcopy

from pydantic import BaseModel, Field

from src.execution_engine import ExecutionEngine
from src.orders import Order
from src.risk import RiskLimitExceeded, RiskManager
import asyncio
from src.live_market import LiveMarket
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.database import get_latest_market_prices
from src.positions import Portfolio


SUPPORTED_PRODUCTS = {
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
}

portfolio = Portfolio()
live_market = LiveMarket(SUPPORTED_PRODUCTS)
execution_engine = ExecutionEngine()
execution_history = []

risk_manager = RiskManager(
    max_order_quantity="2",
    max_position_quantity="5",
    max_order_notional="250000",
    max_realized_loss="5000",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = [
        asyncio.create_task(
            live_market.run_product(product_id)
        )
        for product_id in SUPPORTED_PRODUCTS
    ]

    print("Market Data Engine API started.")

    try:
        yield
    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        print("Market Data Engine API stopped.")


app = FastAPI(
    title="Market Data Engine API",
    description=(
        "Market data, simulated execution, "
        "positions, P&L, and risk API."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class OrderRequest(BaseModel):
    product_id: str
    side: str
    quantity: float = Field(gt=0)


@app.get("/")
def root():
    return {
        "name": "Market Data Engine",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
    }

@app.get("/live/{product_id}")
def live_market_data(product_id: str):
    product_id = product_id.upper()

    if product_id not in SUPPORTED_PRODUCTS:
        raise HTTPException(
            status_code=404,
            detail="Unsupported product.",
        )

    summary = live_market.get_summary(product_id)

    if summary is None:
        raise HTTPException(
            status_code=503,
            detail="Live market is still connecting.",
        )

    return summary

@app.get("/market/{product_id}")
def market_data(
    product_id: str,
    limit: int = 20,
):
    product_id = product_id.upper()

    if product_id not in SUPPORTED_PRODUCTS:
        raise HTTPException(
            status_code=404,
            detail="Unsupported product.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    rows = get_latest_market_prices(
        product_id,
        limit=limit,
    )

    return {
        "product_id": product_id,
        "count": len(rows),
        "data": [
            {
                "recorded_at": recorded_at,
                "symbol": symbol,
                "price": float(price),
                "bid": float(bid),
                "ask": float(ask),
                "spread": float(spread),
            }
            for (
                recorded_at,
                symbol,
                price,
                bid,
                ask,
                spread,
            ) in rows
        ],
    }


@app.get("/positions")
def positions():
    return {
        "positions": [
            {
                "product_id": position.product_id,
                "quantity": float(position.quantity),
                "average_entry_price": float(
                    position.average_entry_price
                ),
                "realized_pnl": float(
                    position.realized_pnl
                ),
            }
            for position in portfolio.positions.values()
        ]
    }

@app.post("/orders")
def submit_order(request: OrderRequest):
    product_id = request.product_id.upper()
    side = request.side.lower()

    if product_id not in SUPPORTED_PRODUCTS:
        raise HTTPException(
            status_code=404,
            detail="Unsupported product.",
        )

    if side not in {"buy", "sell"}:
        raise HTTPException(
            status_code=400,
            detail="Side must be buy or sell.",
        )

    summary = live_market.get_summary(product_id)

    if summary is None:
        raise HTTPException(
            status_code=503,
            detail="Live market is still connecting.",
        )

    order = Order(
        product_id=product_id,
        side=side,
        order_type="market",
        quantity=request.quantity,
    )

    market_price = (
        summary["best_ask"]
        if side == "buy"
        else summary["best_bid"]
    )

    try:
        risk_manager.validate_order(
            order,
            portfolio,
            market_price,
        )

        simulation_book = deepcopy(
            live_market.order_books[product_id]
        )

        executions = (
            execution_engine.execute_market_order(
                order,
                simulation_book,
            )
        )

    except (ValueError, RiskLimitExceeded) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if not executions:
        raise HTTPException(
            status_code=409,
            detail="No liquidity available.",
        )

    for execution in executions:
        portfolio.apply_execution(execution)
        execution_history.append(execution)

    return {
        "order_id": order.order_id,
        "product_id": order.product_id,
        "side": order.side.value,
        "status": order.status.value,
        "quantity": float(order.quantity),
        "filled_quantity": float(
            order.filled_quantity
        ),
        "average_fill_price": float(
            order.average_fill_price
        ),
        "executions": [
            {
                "execution_id": execution.execution_id,
                "quantity": float(execution.quantity),
                "price": float(execution.price),
                "executed_at": execution.executed_at,
            }
            for execution in executions
        ],
    }
@app.get("/executions")
def executions():
    return {
        "executions": [
            {
                "execution_id": execution.execution_id,
                "order_id": execution.order_id,
                "product_id": execution.product_id,
                "side": execution.side.value,
                "quantity": float(execution.quantity),
                "price": float(execution.price),
                "executed_at": execution.executed_at,
            }
            for execution in reversed(execution_history)
        ]
    }