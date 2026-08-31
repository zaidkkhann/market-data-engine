import requests

url = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"
response = requests.get(url, timeout=10)
data = response.json()
price = float(data["price"])
bid = float(data["bid"])
ask = float(data["ask"])
spread = ask - bid

print(f"Symbol: BTC-USD")
print(f"Price: ${price:,.2f}")
print(f"Bid: ${bid:,.2f}")
print(f"Ask: ${ask:,.2f}")
print(f"Spread: ${spread:.2f}")
print(f"Time: {data['time']}")