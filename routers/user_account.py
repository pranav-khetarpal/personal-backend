from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, Path, Query
from firebase_configuration import db
from models.create_user_model import CreateUserModel
from models.user_model import UserModel
from routers.user_interactions import get_current_user_id

# Create a router for the user account related requests
user_account_router = APIRouter()

@user_account_router.post("/user/create", response_model=UserModel)
async def create_user(
    user: CreateUserModel, 
    user_id: str = Depends(get_current_user_id), 
) -> UserModel:
    """
    Endpoint to create a new user
    """
    try:
        # Log extracted user ID
        print(f'Extracted user ID from token: {user_id}')

        # Construct the user data
        user_data = {
            'id': user_id,  # Use the user ID from the token
            'name': user.name,
            'username': user.username,
            'following': []  # Assuming you have a field for 'following'
        }

        # Log user data before saving
        print(f'User data to be saved: {user_data}')

        # Save the user data to the database
        db.collection('users').document(user_id).set(user_data)

        # Return the newly created user data
        return UserModel(**user_data)

    except Exception as e:
        # Handle any unexpected errors
        print(f'Error occurred while creating user: {e}')
        raise HTTPException(status_code=500, detail="Failed to create user: {}".format(str(e)))


@user_account_router.delete("/user/delete")
async def delete_user(user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to delete a user and all of their content on the app
    """
    try:
        print(user_id)
        # Retrieve the user from the Firestore users collection
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete user's posts from the Firestore posts collection
        posts_ref = db.collection('posts').where('userId', '==', user_id)
        posts = posts_ref.stream()

        for post in posts:
            post.reference.delete()

        # Delete the user from the Firestore users collection
        user_ref.delete()

        return {"message": "User and associated data deleted successfully"}

    except Exception as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
