from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import sys

# Add the current directory to sys.path to ensure imports work in Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screener import get_screener_results, DEFAULT_TICKERS

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Renders the main dashboard.
    """
    return templates.TemplateResponse("index.html", {"request": request})

from pydantic import BaseModel
from typing import List

from data import NASDAQ_100, SP_100, SP_500_SAMPLE

class ScanRequest(BaseModel):
    tickers: List[str]

@app.get("/api/tickers")
async def get_tickers():
    """
    Returns available ticker lists.
    """
    return {
        "nasdaq_100": NASDAQ_100,
        "sp_100": SP_100,
        "sp_500": SP_500_SAMPLE
    }

@app.post("/api/scan_batch")
async def run_scan_batch(request: ScanRequest):
    """
    API endpoint to run the screener on a specific batch of tickers.
    """
    # Run screener on the provided batch
    results = get_screener_results(request.tickers)
    return {"results": results}
