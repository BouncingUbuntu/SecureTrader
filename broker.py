import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class BrokerManager:
    """Manages real trading execution via Alpaca API with strict risk guardrails."""
    
    def __init__(self, is_live: bool = False):
        self.is_live = is_live
        
        # Load keys from environment variables for zero-hardcoding security
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Security Error: Missing API keys in environment variables.")

        # Hard safety ceiling: maximum capital allowed per individual trade
        self.MAX_TRADE_DOLLAR_LIMIT = 250.00  

        # Paper trading vs Live trading endpoint routing
        self.client = TradingClient(
            api_key=self.api_key, 
            secret_key=self.secret_key, 
            paper=not self.is_live
        )

    def execute_market_buy(self, symbol: str, qty: int, estimated_price: float):
        total_cost = qty * estimated_price

        # Safeguard 1: Hard Stop on Order Size
        if total_cost > self.MAX_TRADE_DOLLAR_LIMIT:
            return False, f"Risk Blocked: Order value (${total_cost:.2f}) exceeds trade limit (${self.MAX_TRADE_DOLLAR_LIMIT:.2f})."

        # Safeguard 2: Account Buying Power Verification
        account = self.client.get_account()
        if float(account.buying_power) < total_cost:
            return False, f"Execution Blocked: Insufficient funds. Available: ${float(account.buying_power):.2f}"

        # Submit Real/Paper Order to Broker
        try:
            req = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            order = self.client.submit_order(order_data=req)
            return True, f"Order Submitted Successfully. Order ID: {order.id}"
        
        except Exception as e:
            return False, f"API Order Failed: {str(e)}"
