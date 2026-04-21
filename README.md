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

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/trading_bot.git
cd trading_bot
```

**2. Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API credentials**
```bash
cp .env.example .env
```
Open `.env` and fill in your Binance Futures Testnet credentials:

BINANCE_API_KEY=your_testnet_api_key_here \n
BINANCE_API_SECRET=your_testnet_api_secret_here

Get your free testnet credentials at: https://testnet.binancefuture.com

## Usage

### Mode 1 — Interactive Menu (Enhanced CLI UX)
Run without any arguments to get a guided interactive menu with arrow key navigation:
```bash
python cli.py
```
You will be prompted to select order type, side, symbol, quantity and price step by step with validation at each step.

### Mode 2 — Direct Command

**Market BUY:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit SELL:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 75000
```

**Stop-Market SELL (Bonus):**
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --price 60000
```

## Logging
All API requests, responses and errors are automatically logged to: logs/trading_bot_YYYY-MM-DD.log

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
- For Limit orders, price must be realistic (near current market price)
- For Stop-Market orders, stop price must be below current price for SELL, above for BUY