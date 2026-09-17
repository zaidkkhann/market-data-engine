from pathlib import Path


BASE_URL = "https://api.exchange.coinbase.com"
WEBSOCKET_URL = "wss://ws-feed.exchange.coinbase.com"
REQUEST_TIMEOUT_SECONDS = 10
POLL_INTERVAL_SECONDS = 5
DATA_FILE = Path("data/market_data.csv")

SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
}