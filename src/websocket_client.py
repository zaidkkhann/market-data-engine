import asyncio
import json
import time

import websockets

from src.config import WEBSOCKET_URL
from src.database import get_connection, insert_market_price


def normalize_ticker(data):
    return {
        "time": data["time"],
        "price": data["price"],
        "bid": data["best_bid"],
        "ask": data["best_ask"],
    }


async def stream_ticker(product_id):
    subscribe_message = {
        "type": "subscribe",
        "product_ids": [product_id],
        "channels": ["ticker"],
    }

    last_saved_time = 0

    with get_connection() as database_connection:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            await websocket.send(json.dumps(subscribe_message))
            print(f"Connected to live ticker: {product_id}")

            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("type") != "ticker":
                    continue

                print(
                    f'{data["time"]} | {data["product_id"]} | '
                    f'Price: ${float(data["price"]):,.2f} | '
                    f'Bid: ${float(data["best_bid"]):,.2f} | '
                    f'Ask: ${float(data["best_ask"]):,.2f}'
                )

                current_time = time.monotonic()

                if current_time - last_saved_time >= 1:
                    normalized_data = normalize_ticker(data)

                    insert_market_price(
                        product_id,
                        normalized_data,
                        connection=database_connection,
                    )

                    last_saved_time = current_time


def main():
    product_id = input(
        "Choose BTC-USD, ETH-USD, or SOL-USD: "
    ).strip().upper()

    supported_products = {"BTC-USD", "ETH-USD", "SOL-USD"}

    if product_id not in supported_products:
        print("Invalid product.")
        return

    try:
        asyncio.run(stream_ticker(product_id))
    except KeyboardInterrupt:
        print("\nWebSocket stream stopped.")


if __name__ == "__main__":
    main()