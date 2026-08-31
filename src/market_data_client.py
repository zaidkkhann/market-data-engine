import requests


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
    url = f"https://api.exchange.coinbase.com/products/{product_id}/ticker"

    response = requests.get(url, timeout=10)
    data = response.json()

    price = float(data["price"])
    bid = float(data["bid"])
    ask = float(data["ask"])
    spread = ask - bid

    print(f"\nSymbol: {product_id}")
    print(f"Price: ${price:,.2f}")
    print(f"Bid: ${bid:,.2f}")
    print(f"Ask: ${ask:,.2f}")
    print(f"Spread: ${spread:.2f}")
    print(f"Time: {data['time']}")