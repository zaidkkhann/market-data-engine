import asyncio
import json
import logging

import websockets

from src.config import WEBSOCKET_URL
from src.order_book import OrderBook


logger = logging.getLogger(__name__)


class LiveMarket:
    def __init__(self, product_ids):
        self.order_books = {
            product_id: OrderBook(product_id)
            for product_id in product_ids
        }

        self.connected = {
            product_id: False
            for product_id in product_ids
        }

    async def run_product(self, product_id):
        reconnect_delay = 1
        order_book = self.order_books[product_id]

        while True:
            try:
                subscribe_message = {
                    "type": "subscribe",
                    "channels": [
                        {
                            "name": "level2_batch",
                            "product_ids": [product_id],
                        }
                    ],
                }

                async with websockets.connect(
                    WEBSOCKET_URL,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=None,
                ) as websocket:
                    await websocket.send(
                        json.dumps(subscribe_message)
                    )

                    logger.info(
                        "Connected live market: %s",
                        product_id,
                    )

                    reconnect_delay = 1

                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)

                        if data.get("type") == "snapshot":
                            order_book.load_snapshot(
                                data["bids"],
                                data["asks"],
                            )

                            self.connected[product_id] = True

                        elif data.get("type") == "l2update":
                            for side, price, size in data["changes"]:
                                order_book.update(
                                    side,
                                    price,
                                    size,
                                )

                        elif data.get("type") == "error":
                            raise RuntimeError(
                                f"Coinbase error: {data}"
                            )

            except asyncio.CancelledError:
                raise

            except Exception as error:
                self.connected[product_id] = False

                logger.warning(
                    "%s disconnected: %s",
                    product_id,
                    error,
                )

                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(
                    reconnect_delay * 2,
                    30,
                )

    def get_summary(self, product_id):
        order_book = self.order_books[product_id]

        if not self.connected[product_id]:
            return None

        return {
            "product_id": product_id,
            "best_bid": float(order_book.best_bid()),
            "best_ask": float(order_book.best_ask()),
            "spread": float(order_book.spread()),
            "midpoint": float(order_book.midpoint()),
            "bid_levels": len(order_book.bids),
            "ask_levels": len(order_book.asks),
        }
    