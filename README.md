# Market Data Engine

A Python market-data application that retrieves live cryptocurrency prices from the Coinbase Exchange API, tracks price movement, calculates bid-ask spreads, and stores historical observations in CSV format.

## Current Features

- Live market data for BTC-USD, ETH-USD, and SOL-USD
- Continuous REST API polling
- Bid-ask spread calculations
- Upward and downward price-movement tracking
- Persistent CSV storage
- API timeout and error handling
- Structured application logging
- Automated calculation tests

## Project Structure

```text
market-data-engine/
├── src/
│   ├── __init__.py
│   ├── calculations.py
│   ├── config.py
│   └── market_data_client.py
├── tests/
│   └── test_calculations.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

Clone the repository:

```bash
git clone https://github.com/zaidkkhann/market-data-engine.git
cd market-data-engine
```

Create a virtual environment:

```bash
py -m venv .venv
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the Application

```powershell
.\.venv\Scripts\python.exe -m src.market_data_client
```

Choose one of the supported symbols when prompted:

```text
BTC
ETH
SOL
```

Press `Ctrl + C` to stop monitoring.

## Run the Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Roadmap

- PostgreSQL market-data storage
- Real-time WebSocket market feed
- Order book
- Simulated order execution
- Position and P&L tracking
- Risk calculations
- FastAPI endpoints
- Docker and continuous integration

## Data Source

Market data is retrieved from the public Coinbase Exchange API.

## Disclaimer

This project is for software-engineering and educational purposes. It does not execute real financial trades or provide financial advice.
