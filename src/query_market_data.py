from src.config import SYMBOLS
from src.database import get_latest_market_prices


def main():
    choice = input("Choose BTC, ETH, or SOL: ").strip().upper()

    if choice not in SYMBOLS:
        print("Invalid symbol.")
        return

    product_id = SYMBOLS[choice]
    rows = get_latest_market_prices(product_id, limit=5)

    if not rows:
        print(f"No saved data found for {product_id}.")
        return

    print(f"\nLatest saved prices for {product_id}:\n")

    for recorded_at, symbol, price, bid, ask, spread in rows:
        print(
            f"{recorded_at} | {symbol} | "
            f"Price: ${price:,.2f} | "
            f"Bid: ${bid:,.2f} | "
            f"Ask: ${ask:,.2f} | "
            f"Spread: ${spread:,.2f}"
        )


if __name__ == "__main__":
    main()