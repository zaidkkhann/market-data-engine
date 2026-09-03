from src.calculations import calculate_movement, calculate_spread


def test_calculate_spread():
    result = calculate_spread(100.00, 100.05)

    assert round(result, 2) == 0.05

def test_starting_price():
    assert calculate_movement(100.00, None) == "Starting price"


def test_price_moves_up():
    assert calculate_movement(103.00, 100.00) == "UP $3.00"


def test_price_moves_down():
    assert calculate_movement(101.00, 103.00) == "DOWN $2.00"


def test_price_does_not_change():
    assert calculate_movement(100.00, 100.00) == "No change"