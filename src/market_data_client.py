import csv
import time
from src.calculations import calculate_movement, calculate_spread
from pathlib import Path

import requests
DATA_FILE = Path("data/market_data.csv")
def fetch_ticker(product_id):
    url = f"https://api.exchange.coinbase.com/products/{product_id}/ticker"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Coinbase took too long to respond.")

    except requests.exceptions.RequestException as error:
        print(f"Unable to retrieve market data: {error}")

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

if choice not in symbols:
    print("Invalid symbol. Please choose BTC, ETH, or SOL.")
else:
    product_id = symbols[choice]
    previous_price = None

    print(f"\nMonitoring {product_id}. Press Ctrl + C to stop.")

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

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nMarket monitor stopped.")