from pydantic import BaseModel 
from datetime import datetime 

# this is the pydantic model (or object) for a post, needed for data validation
class PostModel(BaseModel):
    id: str
    userId: str
    content: str
    timestamp: datetime
