import asyncio
import json
import time

import websockets

from src.config import WEBSOCKET_URL
from src.order_book import OrderBook


async def stream_order_book(product_id):
    order_book = OrderBook(product_id)

    subscribe_message = {
    "type": "subscribe",
    "channels": [
        {
            "name": "level2_batch",
            "product_ids": [product_id],
        }
    ],
}

    last_display_time = 0

    async with websockets.connect(
        WEBSOCKET_URL,
        ping_interval=20,
        ping_timeout=20,
        max_size=None,
    ) as websocket:
        await websocket.send(json.dumps(subscribe_message))

        print(f"Connected to Level 2 order book: {product_id}")
        print("Waiting for initial snapshot...")

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "snapshot":
                order_book.load_snapshot(
                    data["bids"],
                    data["asks"],
                )

                print(
                    f"Snapshot loaded: "
                    f"{len(order_book.bids):,} bid levels and "
                    f"{len(order_book.asks):,} ask levels"
                )

            elif data.get("type") == "l2update":
                for side, price, size in data["changes"]:
                    order_book.update(side, price, size)

            elif data.get("type") == "subscriptions":
                print("Level 2 subscription confirmed.")

            elif data.get("type") == "error":
                raise RuntimeError(
                    f'Coinbase error: {data.get("message", "Unknown error")}'
                )

            else:
                print(f"Received message type: {data.get('type')}")
                

            current_time = time.monotonic()

            if (
                order_book.best_bid() is not None
                and order_book.best_ask() is not None
                and current_time - last_display_time >= 1
            ):
                print(
                    f"Best bid: ${order_book.best_bid():,.2f} | "
                    f"Best ask: ${order_book.best_ask():,.2f} | "
                    f"Spread: ${order_book.spread():,.2f} | "
                    f"Midpoint: ${order_book.midpoint():,.2f}"
                )

                last_display_time = current_time


def main():
    product_id = input(
        "Choose BTC-USD, ETH-USD, or SOL-USD: "
    ).strip().upper()

    supported_products = {
        "BTC-USD",
        "ETH-USD",
        "SOL-USD",
    }

    if product_id not in supported_products:
        print("Invalid product.")
        return

    try:
        asyncio.run(stream_order_book(product_id))
    except KeyboardInterrupt:
        print("\nOrder-book stream stopped.")


if __name__ == "__main__":
    main()