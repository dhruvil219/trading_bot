# bot/orders.py
from bot.client import BinanceClient
from bot.logging_config import setup_logger

logger = setup_logger()


def print_order_summary(symbol, side, order_type, quantity, price=None):
    print("\n" + "="*50)
    print("        📋 ORDER REQUEST SUMMARY")
    print("="*50)
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price:
        print(f"  Price      : {price}")
    print("="*50 + "\n")


def print_order_response(response: dict):
    print("\n" + "="*50)
    print("        ✅ ORDER RESPONSE")
    print("="*50)
    print(f"  Order ID   : {response.get('orderId', 'N/A')}")
    print(f"  Symbol     : {response.get('symbol', 'N/A')}")
    print(f"  Status     : {response.get('status', 'N/A')}")
    print(f"  Side       : {response.get('side', 'N/A')}")
    print(f"  Type       : {response.get('type', 'N/A')}")
    print(f"  Quantity   : {response.get('origQty', 'N/A')}")
    print(f"  Executed   : {response.get('executedQty', 'N/A')}")
    avg_price = response.get('avgPrice') or response.get('price', 'N/A')
    print(f"  Avg Price  : {avg_price}")
    print("="*50)
    print("  🎉 Order placed successfully!")
    print("="*50 + "\n")


def place_order(client: BinanceClient, symbol: str, side: str,
                order_type: str, quantity: float, price: float = None) -> dict:
    logger.info(f"Placing {order_type} {side} order | {symbol} | qty={quantity}" +
                (f" | price={price}" if price else ""))

    print_order_summary(symbol, side, order_type, quantity, price)

    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price
    )

    logger.info(f"Order SUCCESS | ID={response.get('orderId')} | Status={response.get('status')}")
    print_order_response(response)
    return response