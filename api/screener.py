import yfinance as yf
import pandas as pd
import numpy as np

# Default Tickers (Subset of NASDAQ 100 for MVP/Vercel Performance)
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "PEP",
    "CSCO", "TMUS", "CMCSA", "INTC", "QCOM", "TXN", "AMGN", "HON", "INTU", "SBUX",
    "NFLX", "AMD", "ADBE", "GILD", "PYPL", "MDLZ", "ADP", "ISRG", "REGN", "VRTX"
]

def fetch_data(tickers=DEFAULT_TICKERS, period="1y"):
    """
    Fetches historical data for the given tickers.
    Returns: DataFrame with MultiIndex (Ticker, Date) or similar structure.
    """
    if not tickers:
        return pd.DataFrame()

    # yfinance download is faster with multi-threaded download
    data = yf.download(tickers, period=period, group_by='ticker', progress=False, auto_adjust=True)
    
    # Standardize to MultiIndex DataFrame
    if len(tickers) == 1:
        # If single ticker, yfinance returns columns like [Open, High, Low, Close, Volume]
        # We need to make it hierarchical or just add Ticker column
        df = data.copy()
        df['Ticker'] = tickers[0]
        df = df.reset_index()
        # Rename 'Date' if likely 'Date' is index name
        return df

    # For multiple tickers, column index is (Ticker, PriceType)
    # We want a long format DataFrame: Date, Ticker, Close, ...
    
    # Stack the level 0 (Ticker) to make it a row index
    try:
        data = data.stack(level=0)
        data.index.names = ['Date', 'Ticker']
        data = data.reset_index()
    except Exception:
        # Fallback if structure is different
        pass
        
    return data

def calculate_rsi(series, period=14):
    """
    Calculates RSI using pandas.
    """
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    # Use exponential moving average
    ma_up = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    
    rsi = ma_up / (ma_up + ma_down) * 100
    return rsi

def get_screener_results(tickers=DEFAULT_TICKERS):
    """
    Main function to run the screener using Pandas.
    """
    if not tickers:
        return []

    df = fetch_data(tickers)
    
    if df.empty:
        return []

    # Ensure required columns exist
    # yfinance auto_adjust=True returns 'Close' which is Adjusted Close. 
    # Sometimes columns are capitalizing differently.
    
    # Helper to calculate indicators per ticker
    results = []
    
    # Group by Ticker
    for ticker, group in df.groupby('Ticker'):
        try:
            # Sort by date
            g = group.sort_values('Date').copy()
            
            # Indicators
            g['SMA_50'] = g['Close'].rolling(window=50).mean()
            g['SMA_200'] = g['Close'].rolling(window=200).mean()
            g['RSI'] = calculate_rsi(g['Close'], period=14)
            
            # Historical Volatility (20-day annualized)
            g['Log_Ret'] = np.log(g['Close'] / g['Close'].shift(1))
            g['HV_Rank'] = g['Log_Ret'].rolling(window=20).std() * np.sqrt(252) * 100
            
            # Get latest row
            last_row = g.iloc[-1]
            
            # --- Filters ---
            
            # 1. Liquidity (Vol > 1M)
            if last_row['Volume'] < 1_000_000:
                continue
                
            # 2. Trend (Price > SMA50 & Price > SMA200)
            if not (last_row['Close'] > last_row['SMA_50'] and last_row['Close'] > last_row['SMA_200']):
                continue
                
            # 3. Setup (RSI 40-60)
            if not (40 <= last_row['RSI'] <= 60):
                continue
                
            # Convert to dict
            # Handle NaN values for JSON serialization
            record = last_row.to_dict()
            for k, v in record.items():
                if pd.isna(v):
                    record[k] = None
                    
            results.append(record)
            
        except Exception as e:
            # print(f"Error processing {ticker}: {e}")
            continue

    return results

if __name__ == "__main__":
    # Test locally
    print("Running screener...")
    results = get_screener_results(["AAPL", "TSLA", "NVDA", "AMD"])
    print(f"Found {len(results)} matches.")
    # for r in results:
    #     print(r['Ticker'], r['Close'], r['RSI'])
