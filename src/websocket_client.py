import asyncio
import json

import websockets

from src.config import WEBSOCKET_URL


async def stream_ticker(product_id):
    subscribe_message = {
        "type": "subscribe",
        "product_ids": [product_id],
        "channels": ["ticker"],
    }

    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps(subscribe_message))
        print(f"Connected to live ticker: {product_id}")

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "ticker":
                print(
                    f'{data["time"]} | {data["product_id"]} | '
                    f'Price: ${float(data["price"]):,.2f} | '
                    f'Bid: ${float(data["best_bid"]):,.2f} | '
                    f'Ask: ${float(data["best_ask"]):,.2f}'
                )


def main():
    product_id = input("Choose BTC-USD, ETH-USD, or SOL-USD: ").strip().upper()

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