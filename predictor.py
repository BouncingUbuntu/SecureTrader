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
