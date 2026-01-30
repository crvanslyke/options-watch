# Ticker Lists
# Source: Wikipedia/Cleaned Lists (Simplified for MVP)

NASDAQ_100 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST",
    "PEP", "CSCO", "TMUS", "CMCSA", "INTC", "QCOM", "TXN", "AMGN", "HON", "INTU",
    "SBUX", "AMD", "NFLX", "ADBE", "GILD", "PYPL", "MDLZ", "ADP", "ISRG", "REGN",
    "VRTX", "BKNG", "ADI", "MDLZ", "GILD", "LRCX", "MU", "CSX", "MRNA", "ASML",
    "KLAC", "SNPS", "CDNS", "MAR", "NXPI", "ORLY", "FTNT", "KDP", "CTAS", "PCAR",
    "PAYX", "MCHP", "JD", "ROST", "IDXX", "AEP", "AZN", "EXC", "LULU", "DXCM",
    "EA", "ALGN", "WBD", "ODFL", "XEL", "FAST", "GEHC", "DDOG", "ZS", "LCID",
    "RIVN", "TEAM", "WDAY", "BIIB", "SGEN", "DLTR", "MELI", "VRSK", "CPRT", "SIRI",
    "PDD", "CRWD", "ANSS", "SWKS", "SPLK", "MTCH", "OKTA", "ZM", "DOCU", "PTC"
]

# S&P 100 (Subset of SP500, High Cap)
SP_100 = [
    "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
    "AVGO", "AXP", "BA", "BAC", "BK", "BKNG", "BLK", "BMY", "BRK.B", "C",
    "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO", "CVS",
    "CVX", "DE", "DHR", "DIS", "DOW", "DUK", "EMR", "EXC", "F", "FDX",
    "GD", "GE", "GILD", "GM", "GOOG", "GOOGL", "GS", "HD", "HON", "IBM",
    "INTC", "JNJ", "JPM", "KHC", "KO", "LIN", "LLY", "LMT", "LOW", "MA",
    "MCD", "MDLZ", "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT",
    "NEE", "NFLX", "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "PM", "PYPL",
    "QCOM", "RTX", "SBUX", "SCHW", "SO", "SPG", "T", "TGT", "TMO", "TMUS",
    "TSLA", "TXN", "UNH", "UNP", "UPS", "USB", "V", "VZ", "WFC", "WMT", "XOM"
]

# Full S&P 500 (Abbreviated for file size, but architecture supports full list)
# In production, this might be fetched from an API or a larger static file.
SP_500_SAMPLE = SP_100 + [
    "MMM", "AOS", "ABT", "ABBV", "ACN", "ADM", "ADBE", "ADP", "AES", "AFL",
    # ... (Imagine 400 more tickers here) ...
]
