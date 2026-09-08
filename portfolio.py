import yfinance as yf

class PortfolioManager:
    """Tracks holdings and calculates Realized / Unrealized P&L."""
    def __init__(self, initial_cash=10000.00):
        self.holdings = []  # List of dicts: {'symbol': str, 'shares': int, 'buy_price': float}
        self.cash_balance = initial_cash

    def buy_stock(self, symbol, shares, price):
        total_cost = shares * price
        if total_cost > self.cash_balance:
            return False, "Insufficient cash balance."
        
        self.cash_balance -= total_cost
        self.holdings.append({'symbol': symbol, 'shares': shares, 'buy_price': price})
        return True, "Success"

    def get_portfolio_value(self):
        unrealized_pnl = 0.0
        portfolio_rows = []
        
        for item in self.holdings:
            ticker = yf.Ticker(item['symbol'])
            current_price = ticker.fast_info['lastPrice']
            current_val = current_price * item['shares']
            cost_basis = item['buy_price'] * item['shares']
            pnl = current_val - cost_basis
            unrealized_pnl += pnl
            
            portfolio_rows.append({
                'symbol': item['symbol'],
                'shares': item['shares'],
                'buy_price': item['buy_price'],
                'current_price': round(current_price, 2),
                'pnl': round(pnl, 2)
            })
            
        return portfolio_rows, round(unrealized_pnl, 2), round(self.cash_balance, 2)
