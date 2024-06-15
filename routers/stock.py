from fastapi import APIRouter, HTTPException, Query
from typing import List
import yfinance as yf

from models.stock_model import StockModel

# Create a router for the stock related requests
stock_router = APIRouter()

@stock_router.get("/search/stocks", response_model=List[StockModel])
async def search_stock(ticker: str):
    """
    Endpoint to retrieve stock information.
    Currently, it can only look for a single stock ticker.
    May be able to get around this if you make sure that the search query whenever the user changes the text they input.
    """
    try:
        stock_ticker = yf.Ticker(ticker)
        info = stock_ticker.info
        
        # # Print info to debug
        # print(f"Stock info for {ticker}: {info}")
        
        # Attempt to retrieve price from multiple possible fields
        price = info.get('currentPrice') or info.get('previousClose') or info.get('lastClose', 0.0)
        
        if price == 0.0:
            print(f"Price not found for {ticker}, info: {info}")
        
        stock = StockModel(
            symbol=info.get('symbol', 'N/A'),
            name=info.get('shortName', 'N/A'),
            price=price
        )
        
        return [stock]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found: {e}")

@stock_router.get("/stock/info/{ticker}")
async def get_stock_info(ticker: str):
    try:
        # Fetch stock info using yfinance
        stock_ticker = yf.Ticker(ticker)
        info = stock_ticker.info
        
        # Extract required statistics
        required_info = {
            "current_price": info.get("currentPrice"),
            "open_price": info.get("open"),
            "volume": info.get("volume"),
            "high": info.get("dayHigh"),
            "low": info.get("dayLow"),
            "market_cap": info.get("marketCap"),
            "average_volume": info.get("averageVolume"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "pe_ratio": info.get("trailingPE"),
            "overnight_volume": info.get("regularMarketVolume"),
            "description": info.get("longBusinessSummary"),
            "price": info.get('currentPrice') or info.get('previousClose') or info.get('lastClose', 0.0)
        }
        return required_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock data not found: {e}")


@stock_router.get("/stock/prices")
async def get_stock_prices(tickers: List[str] = Query(...)):
    try:
        prices = {}
        for ticker in tickers:
            # Fetch stock info using yfinance
            stock_ticker = yf.Ticker(ticker)
            info = stock_ticker.info
            # print(f'yfinance.Ticker object <{ticker}>')
            # print(info)
            prices[ticker] = info.get('currentPrice') or info.get('previousClose') or info.get('lastClose', 0.0)
        return prices
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock data not found: {e}")
    