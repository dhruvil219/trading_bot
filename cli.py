# cli.py
import argparse
import os
import sys
from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.validators import validate_inputs
from bot.orders import place_order
from bot.logging_config import setup_logger

# Load .env file (reads BINANCE_API_KEY and BINANCE_API_SECRET)
load_dotenv()
logger = setup_logger()


def get_client() -> BinanceClient:
    """Load API credentials from environment variables."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API credentials not found. Check your .env file.")
        print("❌ ERROR: BINANCE_API_KEY or BINANCE_API_SECRET not set in .env")
        sys.exit(1)

    return BinanceClient(api_key, api_secret)


def build_parser() -> argparse.ArgumentParser:
    """Define all CLI arguments."""
    parser = argparse.ArgumentParser(
        description="🤖 Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  Market BUY:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

  Limit SELL:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 70000

  Stop Market (bonus):
    python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --price 60000
        """
    )
    parser.add_argument("--symbol",   required=True,  help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",     required=True,  help="BUY or SELL")
    parser.add_argument("--type",     required=True,  help="MARKET, LIMIT, or STOP_MARKET",
                        dest="order_type")
    parser.add_argument("--quantity", required=True,  help="Amount to trade, e.g. 0.01")
    parser.add_argument("--price",    required=False, help="Price (required for LIMIT/STOP_MARKET)",
                        default=None)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    logger.info("="*60)
    logger.info("Trading Bot Started")
    logger.info("="*60)

    # Step 1: Validate all inputs
    try:
        validated = validate_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price
        )
    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)

    # Step 2: Create API client
    client = get_client()

    # Step 3: Test connection first
    try:
        client.get_server_time()
        logger.info("Connection to Binance Testnet: OK")
    except Exception as e:
        logger.error(f"Cannot connect to Binance Testnet: {e}")
        print(f"\n❌ Connection Error: {e}\n")
        sys.exit(1)

    # Step 4: Place the order
    try:
        place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated.get("price")
        )
    except RuntimeError as e:
        logger.error(f"Order failed: {e}")
        print(f"\n❌ Order Failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected Error: {e}\n")
        sys.exit(1)

    logger.info("Trading Bot Session Ended")


if __name__ == "__main__":
    main()