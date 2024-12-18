# Pydantic model for the follow request
from pydantic import BaseModel

class FollowRequest(BaseModel):
    userIdToFollow: str

class UnfollowRequest(BaseModel):
    userIdToUnfollow: str
