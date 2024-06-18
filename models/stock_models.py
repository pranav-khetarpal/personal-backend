from pydantic import BaseModel

class StockModel(BaseModel):
    symbol: str
    name: str
    price: float

class StockListUpdateRequest(BaseModel):
    name: str
    tickers: list[str]

class StockListCreateRequest(BaseModel):
    name: str
    tickers: list[str]
