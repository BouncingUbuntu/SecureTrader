import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class StockPredictor:
    """Predicts next-day close price using Linear Regression on short-term trend."""
    @staticmethod
    def get_prediction(ticker_symbol):
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="60d")
        if df.empty or len(df) < 10:
            return None, None
        
        df['Day'] = np.arange(len(df))
        X = df[['Day']]
        y = df['Close']
        
        model = LinearRegression()
        model.fit(X, y)
        
        current_price = df['Close'].iloc[-1]
        next_day = np.array([[len(df)]])
        predicted_price = model.predict(next_day)[0]
        
        return round(float(current_price), 2), round(float(predicted_price), 2)

class PortfolioManager:
    """Tracks holdings and calculates Realized / Unrealized P&L."""
    def __init__(self):
        self.holdings = [] # List of dicts: {'symbol': str, 'shares': int, 'buy_price': float}
        self.cash_balance = 10000.00 # Starting mock cash

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

class StockTradingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Trading Predictor & Portfolio Tracker")
        self.root.geometry("700x550")
        
        self.portfolio = PortfolioManager()
        self.build_ui()

    def build_ui(self):
        # Header / Search Frame
        frame_top = tk.LabelFrame(self.root, text="Stock Predictor Controls", padx=10, pady=10)
        frame_top.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_top, text="Ticker Symbol:").grid(row=0, column=0, str="w")
        self.entry_ticker = tk.Entry(frame_top, width=10)
        self.entry_ticker.insert(0, "AAPL")
        self.entry_ticker.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Shares to Buy:").grid(row=0, column=2, padx=5)
        self.entry_shares = tk.Entry(frame_top, width=5)
        self.entry_shares.insert(0, "5")
        self.entry_shares.grid(row=0, column=3, padx=5)

        btn_analyze = tk.Button(frame_top, text="Run Prediction", command=self.run_prediction)
        btn_analyze.grid(row=0, column=4, padx=10)

        # Status Display
        self.lbl_status = tk.Label(frame_top, text="Enter a ticker and run analysis.", fg="gray")
        self.lbl_status.grid(row=1, column=0, columnspan=5, sticky="w", pady=5)

        # Portfolio Display Frame
        frame_bottom = tk.LabelFrame(self.root, text="Portfolio & Live P&L Tracker", padx=10, pady=10)
        frame_bottom.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_cash = tk.Label(frame_bottom, text="Cash: $10,000.00 | Total P&L: $0.00", font=("Arial", 10, "bold"))
        self.lbl_cash.pack(anchor="w", pady=5)

        self.tree = ttk.Treeview(frame_bottom, columns=("Symbol", "Shares", "Buy Price", "Current Price", "P&L ($)"), show="headings")
        for col in ("Symbol", "Shares", "Buy Price", "Current Price", "P&L ($)"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def run_prediction(self):
        symbol = self.entry_ticker.get().upper().strip()
        try:
            shares = int(self.entry_shares.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid share amount.")
            return

        self.lbl_status.config(text=f"Fetching data for {symbol}...", fg="blue")
        self.root.update()

        current_price, predicted_price = StockPredictor.get_prediction(symbol)
        if current_price is None:
            messagebox.showerror("Error", "Failed to load stock data.")
            return

        delta = round(predicted_price - current_price, 2)
        signal = "BUY" if delta > 0 else "HOLD / SELL"
        self.lbl_status.config(
            text=f"{symbol} Current: ${current_price} | Predicted Next Close: ${predicted_price} ({'+' if delta > 0 else ''}{delta})",
            fg="green" if delta > 0 else "red"
        )

        # Prompt before auto-buying
        if signal == "BUY":
            confirm = messagebox.askyesno(
                "Auto-Buy Confirmation Prompt",
                f"Prediction Signal: BUY\n\n"
                f"Symbol: {symbol}\n"
                f"Current Price: ${current_price}\n"
                f"Predicted Price: ${predicted_price}\n"
                f"Total Cost for {shares} shares: ${round(shares * current_price, 2)}\n\n"
                f"Do you authorize this transaction?"
            )
            
            if confirm:
                success, msg = self.portfolio.buy_stock(symbol, shares, current_price)
                if success:
                    messagebox.showinfo("Executed", f"Successfully purchased {shares} shares of {symbol}!")
                    self.update_portfolio_ui()
                else:
                    messagebox.showerror("Execution Failed", msg)

    def update_portfolio_ui(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows, total_pnl, cash = self.portfolio.get_portfolio_value()
        for item in rows:
            self.tree.insert("", "end", values=(
                item['symbol'],
                item['shares'],
                f"${item['buy_price']:.2f}",
                f"${item['current_price']:.2f}",
                f"${item['pnl']:.2f}"
            ))

        pnl_color = "green" if total_pnl >= 0 else "red"
        self.lbl_cash.config(
            text=f"Available Cash: ${cash:,.2f} | Total P&L: ${total_pnl:,.2f}",
            fg=pnl_color
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = StockTradingGUI(root)
    root.mainloop()
