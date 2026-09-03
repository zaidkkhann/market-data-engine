def calculate_spread(bid, ask):
    return ask - bid


def calculate_movement(price, previous_price):
    if previous_price is None:
        return "Starting price"

    difference = price - previous_price

    if difference > 0:
        return f"UP ${difference:,.2f}"

    if difference < 0:
        return f"DOWN ${abs(difference):,.2f}"

    return "No change"