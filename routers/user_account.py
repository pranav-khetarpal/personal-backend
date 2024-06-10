from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Header, Path, Query
from firebase_configuration import db
from firebase_admin import auth
from models.user_models import UpdateUserModel, UserModel, CreateUserModel
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


# @user_account_router.post("/user/create", response_model=UserModel)
# async def create_user(
#     user: CreateUserModel, 
#     user_id: str = Depends(get_current_user_id), 
# ) -> UserModel:
#     """
#     Endpoint to create a new user
#     """
#     try:
#         # Log extracted user ID
#         print(f'Extracted user ID from token: {user_id}')

#         # Check if email is already registered in Firebase Authentication
#         try:
#             user_record = auth.get_user_by_email(user.email)
#             if user_record:
#                 raise HTTPException(status_code=400, detail="Email is already registered")
#         except auth.UserNotFoundError:
#             # Email is not registered, continue with registration
#             pass

#         # Check if username is already taken
#         username_query = db.collection('users').where('username', '==', user.username).get()
#         if username_query:
#             raise HTTPException(status_code=400, detail="Username is already taken")

#         # Construct the user data
#         user_data = {
#             'id': user_id,  # Use the user ID from the token
#             'name': user.name,
#             'username': user.username,
#             'following': []  # Assuming you have a field for 'following'
#         }

#         # Log user data before saving
#         print(f'User data to be saved: {user_data}')

#         # Save the user data to the database
#         db.collection('users').document(user_id).set(user_data)

#         # Return the newly created user data
#         return UserModel(**user_data)

#     except HTTPException as e:
#         # Handle known errors
#         raise e
#     except Exception as e:
#         # Handle any unexpected errors
#         print(f'Error occurred while creating user: {e}')
#         raise HTTPException(status_code=500, detail="Failed to create user: {}".format(str(e)))


@user_account_router.post("/user/usernameAvailability")
async def username_availability(
    username: str = Body(..., embed=True)
) -> dict:
    """
    Endpoint to check the availability of a username
    """
    try:
        # Check if username is already taken
        username_query = db.collection('users').where('username', '==', username).get()
        if username_query:
            return {"available": False}
        else:
            return {"available": True}
    except Exception as e:
        print(f'Error occurred while checking username availability: {e}')
        raise HTTPException(status_code=500, detail="Failed to check username availability: {}".format(str(e)))



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


@user_account_router.put("/user/update", response_model=UserModel)
async def update_user(
    user: UpdateUserModel, 
    user_id: str = Depends(get_current_user_id), 
) -> UserModel:
    """
    Endpoint to update an existing user
    """
    try:
        # # Log extracted user ID
        # print(f'Extracted user ID from token: {user_id}')

        # Reference to the user document
        user_ref = db.collection('users').document(user_id)

        # Update the user data
        user_data = user.dict()

        # # Log user data before updating
        # print(f'User data to be updated: {user_data}')

        user_ref.update(user_data)

        # Fetch the updated user data
        updated_user = user_ref.get().to_dict()
        
        # Return the updated user data
        return UserModel(**updated_user)

    except Exception as e:
        # Handle any unexpected errors
        print(f'Error occurred while updating user: {e}')
        raise HTTPException(status_code=500, detail="Failed to update user: {}".format(str(e)))
