from pydantic import BaseModel

# New model for post creation that only requires the content field
# This ensures that the ID and timestamp are generated server-side
class CreatePostModel(BaseModel):
    content: str
