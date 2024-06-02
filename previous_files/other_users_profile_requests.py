# from fastapi import FastAPI, HTTPException, APIRouter, Depends, Header
# from firebase_admin import auth, firestore
# from pydantic import BaseModel
# from firebase_configuration import initialize_firebase
# from typing import List

# from firebase_configuration import db
# from models.user_model import User

# # Initialize the Firebase app
# db = initialize_firebase()

# # Create a router for user profile operations
# other_users_profile_router = APIRouter()

# # Helper function to get the current user ID from the token
# def get_current_user_id(token: str = Header(...)) -> str:
#     try:
#         decoded_token = auth.verify_id_token(token)
#         return decoded_token['uid']
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")

# # Pydantic model for the follow request
# class FollowRequest(BaseModel):
#     userIdToFollow: str

# # Route to get the profile of another user by user ID
# @other_users_profile_router.get("/user/{user_id}", response_model=User)
# async def get_user_profile(user_id: str) -> User:
#     """
#     Get the profile information of a user by their user ID.
#     """
#     user_ref = db.collection('users').document(user_id)
#     user_doc = user_ref.get()

#     if user_doc.exists:
#         user_data = user_doc.to_dict()
#         return User(
#             id=user_data['id'],
#             name=user_data['name'],
#             username=user_data['username'],
#             following=user_data['following']
#         )
#     else:
#         raise HTTPException(status_code=404, detail="User not found")

# # Route to follow another user
# @other_users_profile_router.post("/user/follow")
# async def follow_user(follow_request: FollowRequest, user_id: str = Depends(get_current_user_id)):
#     """
#     Add the specified user ID to the current user's following list.
#     """
#     # Get the current user's document reference
#     user_ref = db.collection('users').document(user_id)
#     user_doc = user_ref.get()

#     if not user_doc.exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Get the current user's data
#     user_data = user_doc.to_dict()
#     following = user_data.get('following', [])

#     # Check if the user is already following the target user
#     if follow_request.userIdToFollow in following:
#         raise HTTPException(status_code=400, detail="Already following this user")

#     # Add the target user ID to the following list
#     following.append(follow_request.userIdToFollow)
#     user_ref.update({'following': following})

#     return {"message": "User followed successfully"}
