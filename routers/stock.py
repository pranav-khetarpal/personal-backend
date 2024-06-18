from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import yfinance as yf
from models.stock_models import StockListCreateRequest, StockListUpdateRequest, StockModel
from routers.user_interactions import get_current_user_id
from firebase_configuration import db

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
    """
    Endpoint to return detailed stock information for a given ticker
    """
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
    """
    Endpoint to return the prices of a given list of stock tickers
    """
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






@stock_router.delete("/stock/stockLists/delete/{list_name}", status_code=204)
async def delete_stock_list(list_name: str, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to delete a stock list from a user's document
    """
    try:
        print(list_name)
        # Reference to the user's stockLists subcollection
        stocklists_ref = db.collection('users').document(user_id).collection('stockLists')

        # Query to find the stock list document with the specified name
        query = stocklists_ref.where('name', '==', list_name).stream()

        # Iterate over the query results and delete the matching document
        for doc in query:
            doc.reference.delete()

        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@stock_router.put("/stock/stockLists/update/{list_name}")
async def update_stock_list(list_name: str, request: StockListUpdateRequest, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to update a stock list for a user
    """
    try:
        # Reference to the user's stockLists subcollection
        stocklists_ref = db.collection('users').document(user_id).collection('stockLists')

        # Query to find the stock list document with the specified name
        query = stocklists_ref.where('name', '==', list_name).stream()

        # Update the first matching document with new data
        for doc in query:
            doc.reference.update({
                'name': request.name,
                'tickers': request.tickers,
            })

        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@stock_router.post("/stock/stockLists/create")
async def create_stock_list(request: StockListCreateRequest, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to create a new stock list for a user
    """
    try:
        # Reference to the user's stockLists subcollection
        stocklists_ref = db.collection('users').document(user_id).collection('stockLists')

        # Add new stock list document
        stocklists_ref.add({
            'name': request.name,
            'tickers': request.tickers,
        })

        return {"message": "Stock list created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

