from typing import Optional
from pydantic import BaseModel 
from datetime import datetime 

# this is the pydantic model (or object) for a post, needed for data validation
class PostModel(BaseModel):
    id: str
    userId: str
    content: str
    timestamp: datetime
    likes_count: int
    isLikedByUser: Optional[bool] = False

# New model for post creation that only requires the content field
# This ensures that the ID and timestamp are generated server-side
class CreatePostModel(BaseModel):
    content: str

