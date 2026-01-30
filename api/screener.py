import yfinance as yf
import polars as pl
import pandas as pd
import numpy as np

# Default Tickers (Subset of NASDAQ 100 for MVP/Vercel Performance)
# We limit this to ~20-30 top liquid names to prevent timeouts in the serverless function.
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
    # yfinance download is faster with multi-threaded download
    data = yf.download(tickers, period=period, group_by='ticker', progress=False, auto_adjust=True)
    
    # Process into a clean list of dictionaries or a long-format DataFrame for Polars
    records = []
    
    # yf.download with group_by='ticker' returns a MultiIndex columns dataframe if >1 ticker
    # If standard dataframe (1 ticker), it's just columns.
    
    if len(tickers) == 1:
        # Handle single ticker case
        df = data.copy()
        df['Ticker'] = tickers[0]
        df = df.reset_index()
        records = df.to_dict('records')
    else:
        # Handle multiple tickers
        for ticker in tickers:
            try:
                df = data[ticker].copy()
                if df.empty:
                    continue
                df['Ticker'] = ticker
                df = df.dropna()
                df = df.reset_index()
                # Clean up columns if there are MultiIndex issues or empty data
                records.extend(df.to_dict('records'))
            except KeyError:
                continue

    return records

def calculate_rsi(series, period=14):
    """
    Calculates RSI using Polars expressions.
    Returns a Polars Series.
    """
    delta = series.diff()
    up = delta.clip(lower_bound=0)
    down = delta.clip(upper_bound=0).abs()
    
    # Use EWM for Wilder's smoothing equivalent (com = period - 1)
    # Polars ewm_mean is available.
    roll_up = up.ewm_mean(com=period-1, ignore_nulls=True)
    roll_down = down.ewm_mean(com=period-1, ignore_nulls=True)
    
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_screener_results(tickers=DEFAULT_TICKERS):
    """
    Main function to run the screener.
    """
    raw_data = fetch_data(tickers)
    
    if not raw_data:
        return []

    # Create Polars DataFrame
    # Ensure correct types for 'Date'
    q = (
        pl.DataFrame(raw_data)
        .with_columns(pl.col("Date").cast(pl.Datetime))
        .sort(["Ticker", "Date"])
        .group_by("Ticker")
        .map_groups(lambda df: df.with_columns([
            pl.col("Close").rolling_mean(window_size=50).alias("SMA_50"),
            pl.col("Close").rolling_mean(window_size=200).alias("SMA_200"),
            pl.col("Close").ewm_mean(span=20).alias("EMA_20"),
            
            # RSI Calculation
            calculate_rsi(pl.col("Close"), period=14).alias("RSI")
        ]))
    )
    
    df = q.collect() if hasattr(q, "collect") else q # Handle if lazy or eager

    # Get the latest row for each ticker
    latest_df = df.group_by("Ticker").last()

    # --- Filtering Logic ---
    # 1. Liquidity (approximated by Volume > 1M, simple check on latest volume)
    #    Note: Real implementation might want Avg Volume over 10 days
    latest_df = latest_df.filter(pl.col("Volume") > 1_000_000)

    # 2. Trend: Price > SMA50 and Price > SMA200
    latest_df = latest_df.filter(
        (pl.col("Close") > pl.col("SMA_50")) & 
        (pl.col("Close") > pl.col("SMA_200"))
    )

    # 3. Setup: RSI between 40 and 60 (Pullback Zone)
    latest_df = latest_df.filter(
        (pl.col("RSI") >= 40) & (pl.col("RSI") <= 60)
    )

    # 4. Volatility (Placeholder/Simple Version)
    # We will compute a simple Historical Volatility (HV) over 20 days
    # HV = StdDev(returns) * sqrt(252)
    # Since we are in the 'last()' row context, we can't easily compute rolling std there.
    # We need to compute HV *before* taking the last row.
    
    # ---- RE-DOING PIPELINE TO INCLUDE HV CALCULATION BEFORE FILTERING ----
    
    q_full = (
        pl.DataFrame(raw_data)
         .with_columns(pl.col("Date").cast(pl.Datetime))
        .sort(["Ticker", "Date"])
        .group_by("Ticker")
        .map_groups(lambda sub_df: sub_df.with_columns([
            pl.col("Close").rolling_mean(window_size=50).alias("SMA_50"),
            pl.col("Close").rolling_mean(window_size=200).alias("SMA_200"),
            calculate_rsi(pl.col("Close"), period=14).alias("RSI"),
            
            # HV Calculation (20-day annualized)
            (pl.col("Close").pct_change().rolling_std(window_size=20) * (252 ** 0.5) * 100).alias("HV_Rank") 
            # Note: This is raw HV, not strictly "Rank" (0-100 percentile), but we can use it as a proxy or filter.
            # Real IV Rank requires 52-week High/Low of IV.
            # For this MVP, we will rename this to "Historical_Volatility" and filter if reasonable.
        ]))
    )
    
    # We also need IV (Implied Volatility).
    # Since we can't get history easily efficiently, we will fetch CURRENT IV for the filtered survivors *after* step 3. 
    # Or just return HV for now.
    
    # Let's proceed with the filtered list first using technicals + HV.
    
    df_processed = q_full # Eager
    latest_full = df_processed.group_by("Ticker").last()
    
    # Apply Filters
    filtered = latest_full.filter(
        (pl.col("Volume") > 1_000_000) &
        (pl.col("Close") > pl.col("SMA_50")) &
        (pl.col("Close") > pl.col("SMA_200")) &
        (pl.col("RSI") >= 40) & (pl.col("RSI") <= 60)
    )
    
    # Convert to Python dicts to enrich with yfinance Info (IV) if needed
    results = filtered.to_dicts()
    
    # Enrich with Real-time IV if possible (Optional for Vercel speed, maybe limit to top 5 results?)
    # For now, return the Technical matches.
    
    return results

if __name__ == "__main__":
    # Test locally
    print("Running screener...")
    results = get_screener_results(["AAPL", "TSLA", "NVDA", "AMD"])
    print(f"Found {len(results)} matches.")
    for r in results:
        print(r)
