# SecureTrader 🛡️📈

**SecureTrader** is a desktop application designed for cybersecurity and financial technology portfolios. It demonstrates machine learning trend prediction, strict input sanitization, automated financial guardrails, human-in-the-loop authorization, and secure API integration with [Alpaca Markets](https://alpaca.markets).

---

## 📋 Table of Contents
- [Overview & Key Features](#-overview--key-features)
- [System Architecture](#-system-architecture)
- [Cybersecurity & Risk Guardrails](#-cybersecurity--risk-guardrails)
- [Prerequisites](#-prerequisites)
- [Step-by-Step Setup Guide](#-step-by-step-setup-guide)
  - [1. Obtain Free Alpaca API Keys](#1-obtain-free-alpaca-api-keys)
  - [2. Clone & Install Dependencies](#2-clone--install-dependencies)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Run the Application](#4-run-the-application)
- [Switching to Live Money Execution](#-switching-to-live-money-execution)
- [Resume / Portfolio Highlights](#-resume--portfolio-highlights)
- [Disclaimer](#-disclaimer)

---

## 🚀 Overview & Key Features

* **Machine Learning Predictive Model**: Fits a short-term Linear Regression model using historical daily stock prices (`yfinance`) to identify trend directions.
* **Zero-Trust Human-in-the-Loop Safeguard**: Generates `BUY` signals, but strictly requires explicit user confirmation via a step-up GUI dialog before placing orders.
* **Automated Risk Caps**: Enforces hard-coded maximum single-trade dollar limits ($100.00 default) directly at the code level to prevent fat-finger or catastrophic losses.
* **Input Sanitization & Injection Defense**: Cleanses user input via strict Whitelist Regular Expressions (`^[A-Z]{1,5}$`) and integer range checks.
* **Secret Isolation**: Isolate sensitive credentials using environment variable configuration (`.env`), keeping keys out of version control.
* **Dual Execution Modes**: Seamlessly toggle between Paper Trading (risk-free virtual sandbox) and Live Trading.

---

## 🏗️ System Architecture

```text
SecureTrader/
├── main.py            # GUI, ML predictor, safety validation, & Alpaca API client
├── .env               # Isolated environment credentials (API keys & configuration)
├── .gitignore         # Prevents sensitive files (.env) from being committed
├── requirements.txt   # Python dependency list
└── README.md          # Complete project documentation
```

---

## 🛡️ Cybersecurity & Risk Guardrails

1. **Human-in-the-Loop Zero Trust**: Prevents fully autonomous execution. Every trade signal requires step-up confirmation with order details displayed clearly.
2. **Hard Dollar Safety Guardrail**: Trade value ceiling enforced in Python code regardless of UI inputs or model output.
3. **Input Sanitization**: Rejects malformed tickers, shell parameters, or invalid share quantities prior to processing.
4. **Environment Secret Management**: API keys are retrieved from isolated environment files (`.env`), adhering to Twelve-Factor App security guidelines.

---

## ⚡ Prerequisites

* **Python 3.9+** installed on your system.
* An **Alpaca Trading Account** (Free for Paper Trading).

---

## 📥 Step-by-Step Setup Guide

### 1. Obtain Free Alpaca API Keys

SecureTrader interfaces with Alpaca for order execution. You can start with **Paper Trading** (100% virtual money) without connecting a bank account.

1. Create a free account at [Alpaca.markets](https://alpaca.markets).
2. Log in to your Alpaca Dashboard.
3. On the top panel, ensure your view mode is set to **Paper Trading**.
4. Locate the **API Keys** card on the right sidebar and click **Generate New Keys**.
5. Copy down both your **API Key ID** and **Secret Key**. *(Note: Save the Secret Key immediately as it is only displayed once).*

---

### 2. Clone & Install Dependencies

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/SecureTrader.git
   cd SecureTrader
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Configure Environment Variables

1. Create a file named `.env` in the root folder of the project.
2. Add your Alpaca credentials and initial settings:

```env
# Alpaca Credentials
ALPACA_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
ALPACA_SECRET_KEY="YOUR_ACTUAL_SECRET_KEY_HERE"

# Environment Mode
USE_PAPER_TRADING="True"
```

---

### 4. Run the Application

Launch the desktop interface:
```bash
python main.py
```

**How to interact with the app:**
1. Enter a valid ticker symbol (e.g., `AAPL`, `MSFT`, `NVDA`).
2. Input the desired number of shares.
3. Click **Analyze & Execute**.
4. The system will process historical data, output a prediction, check financial risk caps, and request your step-up authorization if a buy condition is met.

---

## 🔴 Switching to Live Money Execution

To transition from Paper Trading to real capital execution:

1. Complete identity verification on your Alpaca account for Live Trading.
2. Toggle your Alpaca Dashboard to **Live Trading**.
3. Generate a set of **Live API Keys**.
4. Update your `.env` file:
   ```env
   ALPACA_API_KEY="YOUR_LIVE_API_KEY_HERE"
   ALPACA_SECRET_KEY="YOUR_LIVE_SECRET_KEY_HERE"
   USE_PAPER_TRADING="False"
   ```

> ⚠️ **Warning**: Operating with `USE_PAPER_TRADING="False"` will execute orders using REAL CAPITAL. Always test thoroughly in Paper Mode first.

---

## 💼 Resume / Portfolio Highlights

When referencing this project on your resume or cybersecurity portfolio, consider highlighting the following:

* **Engineered a Secure Trading Client**: Applied zero-trust software architecture principles by enforcing step-up manual authorization for automated trading signals.
* **Designed Defensive Financial Guardrails**: Programmed hard-coded single-trade dollar limits and input whitelisting to eliminate parameter tampering and fat-finger execution risk.
* **Hardened Secrets Management**: Implemented environment credential isolation (`.env`) and `.gitignore` guardrails to prevent API key leakage in public repositories.
* **REST API Broker Integration**: Built multi-threaded API pipelines interfacing with Alpaca's trading gateway, supporting seamless paper-to-live execution toggles.

---

## ⚠️ Disclaimer

*This software is developed strictly for educational, research, and portfolio demonstration purposes. Algorithmic trading and financial markets involve substantial risk of loss. Do not trade with capital you cannot afford to lose. The author assumes no responsibility for financial gains or losses incurred through the use of this software.*
