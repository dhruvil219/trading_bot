# cli.py
import argparse
import os
import sys
from dotenv import load_dotenv
import questionary
from questionary import Style

from bot.client import BinanceClient
from bot.validators import validate_inputs
from bot.orders import place_order
from bot.logging_config import setup_logger

load_dotenv()
logger = setup_logger()

# ── Custom style for the interactive menu ──────────────────────
custom_style = Style([
    ("qmark",        "fg:#00ff99 bold"),
    ("question",     "fg:#ffffff bold"),
    ("answer",       "fg:#00ff99 bold"),
    ("pointer",      "fg:#00ff99 bold"),
    ("highlighted",  "fg:#00ff99 bold"),
    ("selected",     "fg:#00ff99"),
    ("separator",    "fg:#444444"),
    ("instruction",  "fg:#888888"),
])


def get_client() -> BinanceClient:
    """Load API credentials from environment variables."""
    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API credentials not found. Check your .env file.")
        print("❌  ERROR: BINANCE_API_KEY or BINANCE_API_SECRET not set in .env")
        sys.exit(1)

    return BinanceClient(api_key, api_secret)


# ── Interactive menu mode ───────────────────────────────────────
def interactive_mode() -> dict:
    """Walk the user through order placement with menus & prompts."""

    print("\n" + "="*52)
    print("   🤖  Binance Futures Testnet Trading Bot")
    print("="*52 + "\n")

    # 1. Order type
    order_type = questionary.select(
        "Select order type:",
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        style=custom_style
    ).ask()
    if order_type is None:
        print("\n👋 Cancelled.")
        sys.exit(0)

    # 2. Side
    side = questionary.select(
        "Select side:",
        choices=["BUY", "SELL"],
        style=custom_style
    ).ask()
    if side is None:
        print("\n👋 Cancelled.")
        sys.exit(0)

    # 3. Symbol
    symbol = questionary.text(
        "Enter symbol:",
        default="BTCUSDT",
        style=custom_style,
        validate=lambda val: True if val.strip().isalpha() and val.strip()
                             else "Symbol must be letters only, e.g. BTCUSDT"
    ).ask()
    if symbol is None:
        print("\n👋 Cancelled.")
        sys.exit(0)

    # 4. Quantity
    quantity = questionary.text(
        "Enter quantity:",
        default="0.01",
        style=custom_style,
        validate=lambda val: True if _is_positive_float(val)
                             else "Please enter a positive number, e.g. 0.01"
    ).ask()
    if quantity is None:
        print("\n👋 Cancelled.")
        sys.exit(0)

    # 5. Price (only for LIMIT / STOP_MARKET)
    price = None
    if order_type in ["LIMIT", "STOP_MARKET"]:
        label = "Enter limit price:" if order_type == "LIMIT" else "Enter stop price:"
        price = questionary.text(
            label,
            style=custom_style,
            validate=lambda val: True if _is_positive_float(val)
                                 else "Please enter a positive number, e.g. 75000"
        ).ask()
        if price is None:
            print("\n👋 Cancelled.")
            sys.exit(0)

    # 6. Confirm
    summary = (
        f"\n  Order Type : {order_type}\n"
        f"  Side       : {side}\n"
        f"  Symbol     : {symbol.upper()}\n"
        f"  Quantity   : {quantity}\n"
    )
    if price:
        summary += f"  Price      : {price}\n"

    print("\n" + "─"*52)
    print(summary)
    print("─"*52)

    confirm = questionary.confirm(
        "Confirm and place this order?",
        default=True,
        style=custom_style
    ).ask()

    if not confirm:
        print("\n👋 Order cancelled.\n")
        sys.exit(0)

    return {
        "symbol":     symbol,
        "side":       side,
        "order_type": order_type,
        "quantity":   quantity,
        "price":      price
    }


def _is_positive_float(val: str) -> bool:
    """Helper: returns True if val is a positive number."""
    try:
        return float(val) > 0
    except ValueError:
        return False


# ── Argument parser (direct command mode) ──────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="🤖 Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Run without arguments for interactive menu mode.

Examples (direct mode):
  Market BUY:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

  Limit SELL:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 75000

  Stop Market:
    python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --price 60000
        """
    )
    parser.add_argument("--symbol",   required=False, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",     required=False, help="BUY or SELL")
    parser.add_argument("--type",     required=False, help="MARKET, LIMIT, or STOP_MARKET",
                        dest="order_type")
    parser.add_argument("--quantity", required=False, help="Amount to trade, e.g. 0.01")
    parser.add_argument("--price",    required=False, help="Price for LIMIT/STOP_MARKET",
                        default=None)
    return parser


# ── Main ────────────────────────────────────────────────────────
def main():
    parser = build_parser()
    args = parser.parse_args()

    logger.info("="*60)
    logger.info("Trading Bot Started")
    logger.info("="*60)

    # Decide mode: if no arguments passed → interactive menu
    if not any([args.symbol, args.side, args.order_type, args.quantity]):
        raw = interactive_mode()
    else:
        # Direct command mode — all required args must be present
        missing = [f"--{k}" for k, v in {
            "symbol": args.symbol,
            "side": args.side,
            "type": args.order_type,
            "quantity": args.quantity
        }.items() if not v]

        if missing:
            print(f"\n❌  Missing arguments: {', '.join(missing)}")
            print("    Tip: run without arguments for interactive mode\n")
            sys.exit(1)

        raw = {
            "symbol":     args.symbol,
            "side":       args.side,
            "order_type": args.order_type,
            "quantity":   args.quantity,
            "price":      args.price
        }

    # Validate inputs
    try:
        validated = validate_inputs(
            symbol=raw["symbol"],
            side=raw["side"],
            order_type=raw["order_type"],
            quantity=raw["quantity"],
            price=raw.get("price")
        )
    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        print(f"\n❌  Validation Error: {e}\n")
        sys.exit(1)

    # Connect
    client = get_client()
    try:
        client.get_server_time()
        logger.info("Connection to Binance Testnet: OK")
    except Exception as e:
        logger.error(f"Cannot connect to Binance Testnet: {e}")
        print(f"\n❌  Connection Error: {e}\n")
        sys.exit(1)

    # Place order
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
        print(f"\n❌  Order Failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌  Unexpected Error: {e}\n")
        sys.exit(1)

    logger.info("Trading Bot Session Ended")


if __name__ == "__main__":
    main()