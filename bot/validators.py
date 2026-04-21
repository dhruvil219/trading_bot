# bot/validators.py

VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT", "STOP_MARKET"]

def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalpha():
        raise ValueError(f"Symbol '{symbol}' looks invalid. Example: BTCUSDT")
    return symbol

def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}. Got: '{side}'")
    return side

def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be one of {VALID_ORDER_TYPES}. Got: '{order_type}'")
    return order_type

def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except ValueError:
        raise ValueError(f"Quantity must be a number. Got: '{quantity}'")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty}")
    return qty

def validate_price(price: str) -> float:
    try:
        p = float(price)
    except ValueError:
        raise ValueError(f"Price must be a number. Got: '{price}'")
    if p <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {p}")
    return p

def validate_inputs(symbol, side, order_type, quantity, price=None):
    validated = {
        "symbol":     validate_symbol(symbol),
        "side":       validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity":   validate_quantity(quantity),
    }

    if validated["order_type"] in ["LIMIT", "STOP_MARKET"]:
        if price is None:
            raise ValueError(f"Price is required for {validated['order_type']} orders.")
        validated["price"] = validate_price(price)
    else:
        validated["price"] = None

    return validated