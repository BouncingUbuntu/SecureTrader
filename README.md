# StockTrader

**StockTrader** is a Python desktop application that predicts short-term stock price trends using machine learning, prompts for user authorization before placing buy orders, and tracks portfolio performance and live P&L in real time.

---

## Features

* **Trend Prediction Engine**: Fits a Linear Regression model on historical stock price data (`yfinance`) to project next-day closing trends.
* **Human-in-the-Loop Safeguard**: Generates `BUY` or `HOLD / SELL` signals, but explicitly requests user confirmation via a popup before executing any transaction.
* **Live Portfolio & P&L Tracker**: Tracks open positions, calculates live market values, and updates overall profit and loss (P&L) dynamically.
* **Lightweight GUI**: Built with standard Python `tkinter` for cross-platform desktop UI execution without external visual frameworks.

---

## Directory Structure

```text
StockTrader/
├── app.py             # Main Tkinter GUI and application driver
├── predictor.py       # Scikit-learn trend prediction logic
├── portfolio.py       # Portfolio management and P&L calculations
├── requirements.txt   # Python dependency list
└── README.md          # Project documentation
