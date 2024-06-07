from pydantic import BaseModel

class StockModel(BaseModel):
    symbol: str
    name: str
    price: float
    