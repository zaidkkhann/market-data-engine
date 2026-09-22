import pytest

from src.websocket_client import normalize_ticker


def test_normalize_ticker():
    websocket_data = {
        "time": "2026-09-22T12:00:00Z",
        "price": "77282.56",
        "best_bid": "77282.55",
        "best_ask": "77282.57",
    }

    result = normalize_ticker(websocket_data)

    assert result == {
        "time": "2026-09-22T12:00:00Z",
        "price": "77282.56",
        "bid": "77282.55",
        "ask": "77282.57",
    }


def test_normalize_ticker_does_not_modify_original_data():
    websocket_data = {
        "time": "2026-09-22T12:00:00Z",
        "price": "77282.56",
        "best_bid": "77282.55",
        "best_ask": "77282.57",
    }

    normalize_ticker(websocket_data)

    assert "best_bid" in websocket_data
    assert "best_ask" in websocket_data
    assert "bid" not in websocket_data
    assert "ask" not in websocket_data


def test_normalize_ticker_rejects_missing_fields():
    incomplete_data = {
        "time": "2026-09-22T12:00:00Z",
        "price": "77282.56",
    }

    with pytest.raises(KeyError):
        normalize_ticker(incomplete_data)