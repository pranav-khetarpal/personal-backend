from pydantic import BaseModel

# this is the pydantic model (or object) for a user, needed for data validation
class UserModel(BaseModel):
    id: str
    name: str
    username: str
    following: list[str]

# New model for user creation that only requires the name and username fields
class CreateUserModel(BaseModel):
    name: str
    email: str
    username: str

# Define the update user model
class UpdateUserModel(BaseModel):
    name: str
    username: str
