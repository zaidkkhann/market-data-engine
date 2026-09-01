import time

import requests

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


def display_ticker(product_id, data, previous_price):
    price = float(data["price"])
    bid = float(data["bid"])
    ask = float(data["ask"])
    spread = ask - bid

    if previous_price is None:
        movement = "Starting price"
    else:
        difference = price - previous_price

        if difference > 0:
            movement = f"UP ${difference:,.2f}"
        elif difference < 0:
            movement = f"DOWN ${abs(difference):,.2f}"
        else:
            movement = "No change"

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
                previous_price = display_ticker(
                    product_id,
                    data,
                    previous_price,
                )

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nMarket monitor stopped.")