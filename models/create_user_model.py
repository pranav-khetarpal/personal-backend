from pydantic import BaseModel

# New model for user creation that only requires the name and username fields
class CreateUserModel(BaseModel):
    name: str
    email: str
    username: str
    