import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Load environment variables from .env file
load_dotenv()

class SecureTraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureTrader - Automated Real Execution Bot")
        self.root.geometry("650x500")

        # Configuration Guardrails
        self.MAX_TRADE_DOLLAR_CAP = 100.00  # Hard ceiling on single trade size ($)
        self.USE_PAPER_TRADING = os.getenv("USE_PAPER_TRADING", "True").lower() == "true"
        
        # Load Alpaca API Keys
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")

        self.trading_client = None
        self.init_broker()
        self.build_ui()

    def init_broker(self):
        """Initializes Alpaca API client with credential verification."""
        if not self.api_key or not self.secret_key or "YOUR_API_KEY" in self.api_key:
            messagebox.showwarning(
                "API Keys Missing", 
                "Alpaca API credentials not found in .env file.\nThe app will run in view-only mode."
            )
            return

        try:
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.secret_key,
                paper=self.USE_PAPER_TRADING
            )
        except Exception as e:
            messagebox.showerror("Broker Connection Error", f"Failed to connect to Alpaca: {e}")

    def sanitize_input(self, ticker: str, shares_str: str):
        """Input sanitization and security boundary validation."""
        clean_ticker = ticker.strip().upper()
        if not re.match(r"^[A-Z]{1,5}$", clean_ticker):
            raise ValueError("Invalid Ticker: Must be 1 to 5 letters only.")
        
        try:
            shares = int(shares_str)
            if shares <= 0 or shares > 500:
                raise ValueError()
        except ValueError:
            raise ValueError("Invalid Shares: Must be a positive integer between 1 and 500.")

        return clean_ticker, shares

    def predict_price(self, symbol: str):
        """Predicts next close price using short-term Linear Regression."""
        df = yf.Ticker(symbol).history(period="60d")
        if df.empty or len(df) < 10:
            return None, None
        
        df['Day'] = np.arange(len(df))
        X = df[['Day']]
        y = df['Close']
        
        model = LinearRegression()
        model.fit(X, y)
        
        current_price = round(float(df['Close'].iloc[-1]), 2)
        predicted_price = round(float(model.predict(np.array([[len(df)]]))[0]), 2)
        return current_price, predicted_price

    def build_ui(self):
        mode_text = "MODE: PAPER TRADING (SIMULATION)" if self.USE_PAPER_TRADING else "MODE: LIVE MONEY TRADING"
        lbl_mode = tk.Label(self.root, text=mode_text, fg="blue" if self.USE_PAPER_TRADING else "red", font=("Arial", 10, "bold"))
        lbl_mode.pack(pady=5)

        # Control Panel
        frame_controls = tk.LabelFrame(self.root, text="Order & Prediction Controls", padx=10, pady=10)
        frame_controls.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_controls, text="Ticker:").grid(row=0, column=0)
        self.entry_ticker = tk.Entry(frame_controls, width=8)
        self.entry_ticker.insert(0, "AAPL")
        self.entry_ticker.grid(row=0, column=1, padx=5)

        tk.Label(frame_controls, text="Shares:").grid(row=0, column=2)
        self.entry_shares = tk.Entry(frame_controls, width=5)
        self.entry_shares.insert(0, "1")
        self.entry_shares.grid(row=0, column=3, padx=5)

        btn_run = tk.Button(frame_controls, text="Analyze & Execute", command=self.process_trade)
        btn_run.grid(row=0, column=4, padx=10)

        # Output Box
        self.txt_log = tk.Text(self.root, height=18, width=75)
        self.txt_log.pack(padx=10, pady=10)
        self.log(f"System Initialized. Maximum single-trade cap: ${self.MAX_TRADE_DOLLAR_CAP:.2f}")

    def log(self, text: str):
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)

    def process_trade(self):
        # Step 1: Input Validation
        try:
            symbol, shares = self.sanitize_input(self.entry_ticker.get(), self.entry_shares.get())
        except ValueError as err:
            messagebox.showerror("Security Validation Error", str(err))
            return

        # Step 2: Prediction Analysis
        self.log(f"\nAnalyzing stock data for {symbol}...")
        self.root.update()
        current_price, predicted_price = self.predict_price(symbol)

        if not current_price:
            messagebox.showerror("Error", f"Could not retrieve historical data for {symbol}.")
            return

        total_cost = shares * current_price
        self.log(f"Current Price: ${current_price:.2f} | Predicted Price: ${predicted_price:.2f}")
        self.log(f"Estimated Order Value: ${total_cost:.2f}")

        # Step 3: Hard Dollar Safety Guardrail Check
        if total_cost > self.MAX_TRADE_DOLLAR_CAP:
            msg = f"Security Block: Order total (${total_cost:.2f}) exceeds trade limit cap (${self.MAX_TRADE_DOLLAR_CAP:.2f})."
            self.log(msg)
            messagebox.showwarning("Risk Blocked", msg)
            return

        if predicted_price <= current_price:
            self.log("Prediction Signal: NO BUY (Model projects price decline or neutral movement).")
            return

        # Step 4: Step-Up User Authorization Prompt
        if not self.trading_client:
            messagebox.showwarning("No API Connection", "Broker API not connected. Transaction skipped.")
            return

        target_env = "PAPER ACCOUNT" if self.USE_PAPER_TRADING else "REAL MONEY ACCOUNT"
        confirm = messagebox.askyesno(
            "Authorize Order Execution",
            f"SIGNAL: BUY\n\n"
            f"Target: {symbol}\n"
            f"Shares: {shares}\n"
            f"Estimated Price: ${current_price:.2f}\n"
            f"Total Cost: ${total_cost:.2f}\n"
            f"Destination: {target_env}\n\n"
            f"Authorize execution?"
        )

        # Step 5: Order Submission
        if confirm:
            try:
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=shares,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                order = self.trading_client.submit_order(order_data=order_data)
                self.log(f"SUCCESS: Order submitted! Order ID: {order.id}")
                messagebox.showinfo("Executed", f"Order submitted successfully!\nID: {order.id}")
            except Exception as e:
                self.log(f"EXECUTION FAILURE: {e}")
                messagebox.showerror("API Error", f"Failed to execute order: {e}")
        else:
            self.log("User rejected trade authorization request.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureTraderApp(root)
    root.mainloop()
