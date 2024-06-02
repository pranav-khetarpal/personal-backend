from pydantic import BaseModel

# this is the pydantic model (or object) for a user, needed for data validation
class UserModel(BaseModel):
    id: str
    name: str
    username: str
    following: list[str]
