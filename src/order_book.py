from decimal import Decimal


class OrderBook:
    def __init__(self, product_id):
        self.product_id = product_id
        self.bids = {}
        self.asks = {}

    def load_snapshot(self, bids, asks):
        self.bids.clear()
        self.asks.clear()

        for price, size in bids:
            self.update("buy", price, size)

        for price, size in asks:
            self.update("sell", price, size)

    def update(self, side, price, size):
        price = Decimal(str(price))
        size = Decimal(str(size))

        if side == "buy":
            book_side = self.bids
        elif side == "sell":
            book_side = self.asks
        else:
            raise ValueError("Side must be 'buy' or 'sell'.")

        if size == 0:
            book_side.pop(price, None)
        else:
            book_side[price] = size

    def best_bid(self):
        if not self.bids:
            return None

        return max(self.bids)

    def best_ask(self):
        if not self.asks:
            return None

        return min(self.asks)

    def spread(self):
        bid = self.best_bid()
        ask = self.best_ask()

        if bid is None or ask is None:
            return None

        return ask - bid

    def midpoint(self):
        bid = self.best_bid()
        ask = self.best_ask()

        if bid is None or ask is None:
            return None

        return (bid + ask) / Decimal("2")

    def get_top_levels(self, depth=5):
        top_bids = sorted(
            self.bids.items(),
            key=lambda level: level[0],
            reverse=True,
        )[:depth]

        top_asks = sorted(
            self.asks.items(),
            key=lambda level: level[0],
        )[:depth]

        return {
            "bids": top_bids,
            "asks": top_asks,
        }


if __name__ == "__main__":
    book = OrderBook("BTC-USD")

    book.update("buy", "77280.00", "0.50")
    book.update("buy", "77281.00", "0.25")
    book.update("sell", "77282.00", "0.40")
    book.update("sell", "77283.00", "0.75")

    print(f"Best bid: ${book.best_bid():,.2f}")
    print(f"Best ask: ${book.best_ask():,.2f}")
    print(f"Spread: ${book.spread():,.2f}")
    print(f"Midpoint: ${book.midpoint():,.2f}")
    print(f"Top levels: {book.get_top_levels()}")