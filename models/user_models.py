# from typing import Dict, List, Optional
# from pydantic import BaseModel

# # Pydantic model for user, needed for data validation
# class UserModel(BaseModel):
#     id: str
#     name: str
#     username: str
#     bio: str
#     profile_image_url: str
#     following: List[str]
#     stockLists: Optional[Dict[str, List[str]]] = None  # Set default to None

# # Model for user creation that only requires the name and username fields
# class CreateUserModel(BaseModel):
#     name: str
#     username: str
#     profile_image_url: str
#     bio: str = ""  # Default value for bio

# # Define the update user model
# class UpdateUserModel(BaseModel):
#     name: str
#     username: str
#     bio: str = ""

from typing import Dict, Optional, List
from pydantic import BaseModel

# Pydantic model for user, needed for data validation
class UserModel(BaseModel):
    id: str
    name: str
    username: str
    bio: str
    profile_image_url: str
    followers_count: int = 0
    following_count: int = 0
    stockLists: Optional[Dict[str, List[str]]] = None  # Set default to None

# Model for user creation that only requires the name and username fields
class CreateUserModel(BaseModel):
    name: str
    username: str
    profile_image_url: str
    bio: str = ""  # Default value for bio

# Define the update user model
class UpdateUserModel(BaseModel):
    name: str
    username: str
    bio: str = ""
