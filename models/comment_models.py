from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CommentModel(BaseModel):
    id: str
    userId: str
    content: str
    timestamp: datetime
    likes_count: int
    isLikedByUser: Optional[bool] = False


class CreateCommentModel(BaseModel):
    postId: str
    content: str
