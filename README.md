# OptionsWatch - Lean Call Options Screener

A serverless, high-performance dashboard to scan the **S&P 500** and **NASDAQ 100** for high-probability Call Option setups.

Deployed on **Vercel** + **FastAPI**.

## 🚀 Features

- **Market-Wide Scan**: Scans 500+ tickers in batches to avoid serverless timeouts.
- **Trend "Gatekeeper"**: Filters for stocks in a confirmed uptrend (Price > SMA50 & SMA200).
- **Setup Detector**: Identifies "Pullbacks" within the trend using RSI (40-60).
- **Volatility Analysis**: Color-coded categorization of Historical Volatility to help select the right option strategy.
- **Export to CSV**: Select specific results and download them as a CSV file for detailed analysis.

## 📖 User Guide

### Understanding the Indicators

The dashboard provides 3 key signals for every ticker:

#### 1. Trend (Bullish)
*   **Green Badge**: The stock price is **ABOVE** both its 50-day and 200-day Moving Averages.
*   **Meaning**: The stock is winning. We only look for long entries (Call Options) on stocks that are already in a long-term uptrend.

#### 2. RSI (Relative Strength Index)
*   **Green (40-60)**: **"The Pullback Zone"**. This is the sweet spot. The stock is in an uptrend but has dipped slightly, offering a high-probability entry point.
*   **Red (<30 or >70)**: **Extreme**.
    *   *>70 (Overbought)*: Too expensive, risk of a drop.
    *   *<30 (Oversold)*: Panic selling, risky to catch a falling knife.
*   **Yellow**: Neutral range.

#### 3. Volatility (20-Day Historical)
*   **Green (<30%)**: **Calm/Cheap**. The stock is stable. Option premiums are likely lower. *Good for buying directional calls.*
*   **Yellow (30-50%)**: Moderate volatility.
*   **Red (>50%)**: **Volatile/Expensive**. The stock is moving violently. Option premiums will be high (expensive). *Consider spreads or waiting.*

## 🛠 Local Development

1.  **Install Dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run the Server**:
    ```bash
    uvicorn api.index:app --reload
    ```

3.  **Open Dashboard**:
    Visit `http://localhost:8000`

## ☁️ Deployment (Vercel)

This project is configured for Vercel.

1.  Push to GitHub.
2.  Import project in Vercel.
3.  Deploy (No special environment variables required for standard scan).

**Note on Sharing**: The Vercel deployment URL (e.g., `options-watch.vercel.app`) is **public**. You can share it with anyone, and they can run scans from their browser.
