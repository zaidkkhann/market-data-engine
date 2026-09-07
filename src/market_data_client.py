import csv
import time
import logging
import requests

from src.calculations import calculate_movement, calculate_spread
from src.config import (
    BASE_URL,
    DATA_FILE,
    POLL_INTERVAL_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    SYMBOLS,
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",)

logger = logging.getLogger(__name__)
def fetch_ticker(product_id):
    url = f"{BASE_URL}/products/{product_id}/ticker"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Coinbase took too long to respond.")

    except requests.exceptions.RequestException as error:
        logger.error("Unable to retrieve market data: %s", error)

    return None

def save_ticker(product_id, data):
    DATA_FILE.parent.mkdir(exist_ok=True)

    file_exists = DATA_FILE.exists()

    price = float(data["price"])
    bid = float(data["bid"])
    ask = float(data["ask"])
    spread = calculate_spread(bid, ask)

    with DATA_FILE.open("a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                ["time", "symbol", "price", "bid", "ask", "spread"]
            )

        writer.writerow(
            [
                data["time"],
                product_id,
                price,
                bid,
                ask,
                spread,
            ]
        )

def display_ticker(product_id, data, previous_price):
    price = float(data["price"])
    bid = float(data["bid"])
    ask = float(data["ask"])
    spread = calculate_spread(bid, ask)

    movement = calculate_movement(price, previous_price)

    print(f"\nSymbol: {product_id}")
    print(f"Price: ${price:,.2f}")
    print(f"Movement: {movement}")
    print(f"Bid: ${bid:,.2f}")
    print(f"Ask: ${ask:,.2f}")
    print(f"Spread: ${spread:.2f}")
    print(f"Time: {data['time']}")

    return price

symbols = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
}

choice = input("Choose BTC, ETH, or SOL: ").strip().upper()

if choice not in SYMBOLS:
    logger.warning("Invalid symbol selected: %s", choice)
else:
    product_id = SYMBOLS[choice]
    previous_price = None

    logger.info("Started monitoring %s. Press Ctrl + C to stop.", product_id)

    try:
        while True:
            data = fetch_ticker(product_id)

            if data is not None:
                save_ticker(product_id, data)
                previous_price = display_ticker(
                    product_id,
                    data,
                    previous_price,
                )

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Market monitor stopped.")