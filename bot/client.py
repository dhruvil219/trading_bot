# bot/client.py
import hashlib
import hmac
import time
import requests
from urllib.parse import urlencode
from bot.logging_config import setup_logger

logger = setup_logger()

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """
    Wrapper around Binance Futures Testnet REST API.
    Handles authentication (API key + HMAC signature) automatically.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = TESTNET_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        })

    def _sign(self, params: dict) -> dict:
        """Signs the request with HMAC-SHA256 using your API secret."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> dict:
        """Parse response and raise error if Binance returned an error code."""
        try:
            data = response.json()
        except Exception:
            raise RuntimeError(f"Non-JSON response from Binance: {response.text}")

        if response.status_code != 200:
            code = data.get("code", "unknown")
            msg = data.get("msg", "Unknown error")
            raise RuntimeError(f"Binance API Error [{code}]: {msg}")

        return data

    def get_server_time(self) -> dict:
        """Public endpoint to test connection — no signature needed."""
        url = f"{self.base_url}/fapi/v1/time"
        logger.debug(f"GET {url}")
        response = self.session.get(url)
        return self._handle_response(response)

    def place_order(self, symbol: str, side: str, order_type: str,
                    quantity: float, price: float = None) -> dict:
        """Places an order on Binance Futures Testnet."""
        url = f"{self.base_url}/fapi/v1/order"

        params = {
            "symbol":   symbol,
            "side":     side,
            "type":     order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = "GTC"

        if order_type == "STOP_MARKET":
            if price is None:
                raise ValueError("Stop price is required for STOP_MARKET orders.")
            params["stopPrice"] = price

        params = self._sign(params)

        logger.debug(f"POST {url} | Params: { {k: v for k, v in params.items() if k != 'signature'} }")

        try:
            response = self.session.post(url, params=params)
            data = self._handle_response(response)
            logger.debug(f"Response: {data}")
            return data
        except RuntimeError as e:
            logger.error(f"Order placement failed: {e}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error("Network error: Could not connect to Binance Testnet.")
            raise RuntimeError("Network error: Check your internet connection.")
        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise RuntimeError("Request timed out. Try again.")