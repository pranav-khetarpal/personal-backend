from pydantic import BaseModel
from typing import List

class StockModel(BaseModel):
    symbol: str
    name: str
    price: float

class StockListUpdateRequest(BaseModel):
    name: str
    tickers: List[str]

class StockListCreateRequest(BaseModel):
    name: str
    tickers: List[str]
