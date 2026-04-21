# 🤖 Binance Futures Testnet Trading Bot

A lightweight Python CLI application to place **Market**, **Limit**, and **Stop-Market** 
orders on Binance Futures Testnet (USDT-M). Built with clean, modular code, structured 
logging, and robust error handling.

## Features
- ✅ Place Market and Limit orders via CLI
- ✅ Supports BUY and SELL sides
- ✅ Bonus: Stop-Market orders
- ✅ Input validation with clear error messages
- ✅ Logs all API requests, responses and errors to file
- ✅ Secure — API keys stored in .env, never hardcoded
- ✅ Clean modular structure (client / orders / validators / logging)

## Setup

1. Clone the repo
2. Create virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Testnet API credentials:
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

Get credentials at: https://testnet.binancefuture.com

## Usage

### Market Order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit Order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 70000
```

### Stop Market (Bonus)
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --price 60000
```

## Project Structure
trading_bot/
bot/
client.py         # Binance API wrapper (HMAC signing, HTTP calls)
orders.py         # Order logic and output formatting
validators.py     # Input validation
logging_config.py # Dual logging (file + console)
cli.py              # CLI entry point (argparse)
logs/               # Auto-created log files

## Assumptions
- Tested on Binance Futures USDT-M Testnet only
- Minimum quantity for BTCUSDT is 0.001
- Prices for Limit orders should be realistic (near market price) to avoid rejection