import asyncio
import json
import logging
import time

import psycopg
import websockets
from websockets.exceptions import ConnectionClosed

from src.config import WEBSOCKET_URL
from src.database import get_connection, insert_market_price


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def normalize_ticker(data):
    return {
        "time": data["time"],
        "price": data["price"],
        "bid": data["best_bid"],
        "ask": data["best_ask"],
    }


async def consume_stream(product_id):
    subscribe_message = {
        "type": "subscribe",
        "product_ids": [product_id],
        "channels": ["ticker"],
    }

    last_saved_time = 0

    with get_connection() as database_connection:
        async with websockets.connect(
            WEBSOCKET_URL,
            ping_interval=20,
            ping_timeout=20,
        ) as websocket:
            await websocket.send(json.dumps(subscribe_message))
            logger.info("Connected to live ticker: %s", product_id)

            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("type") != "ticker":
                    continue

                logger.info(
                    "%s | Price: $%.2f | Bid: $%.2f | Ask: $%.2f",
                    data["product_id"],
                    float(data["price"]),
                    float(data["best_bid"]),
                    float(data["best_ask"]),
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


async def stream_ticker(product_id):
    reconnect_delay = 1

    while True:
        try:
            await consume_stream(product_id)
            reconnect_delay = 1

        except (
            ConnectionClosed,
            OSError,
            psycopg.Error,
            json.JSONDecodeError,
            KeyError,
            ValueError,
        ) as error:
            logger.warning(
                "Stream interrupted: %s. Reconnecting in %s seconds...",
                error,
                reconnect_delay,
            )

            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 30)


def main():
    product_id = input(
        "Choose BTC-USD, ETH-USD, or SOL-USD: "
    ).strip().upper()

    supported_products = {"BTC-USD", "ETH-USD", "SOL-USD"}

    if product_id not in supported_products:
        logger.error("Invalid product.")
        return

    try:
        asyncio.run(stream_ticker(product_id))
    except KeyboardInterrupt:
        logger.info("WebSocket stream stopped.")


if __name__ == "__main__":
    main()