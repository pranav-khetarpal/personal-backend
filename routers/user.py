from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, Path, Query
from firebase_admin import auth

from firebase_configuration import db
from models.create_user_model import CreateUserModel
from models.follow_request_model import FollowRequest
from models.user_model import UserModel

# Create a router for the user information related requests
user_router = APIRouter()

# def get_current_user_id(token: str = Header(...)) -> str:
#     """
#     Helper function to get current user ID from token
#     """
#     try:
#         # decodes the token and verifies it
#         decoded_token = auth.verify_id_token(token)

#         # Returns the user ID (uid) if the token is valid
#         return decoded_token['uid']
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(authorization: str = Header(...)) -> str:
    """
    Helper function to get current user ID from token
    """
    try:
        token = authorization.split(" ")[1]
        
        # decodes the token and verifies it
        decoded_token = auth.verify_id_token(token)

        # Returns the user ID (uid) if the token is valid
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# Route to create a new user document
@user_router.post("/user/create", response_model=UserModel)
async def create_user(
    user: CreateUserModel, 
    authorization: str = Header(...), 
) -> UserModel:
    """
    Endpoint to create a new user
    """
    try:
        token = authorization.split(" ")[1]

        # Extract user ID from the token using the get_current_user_id helper function
        user_id_from_token = get_current_user_id(token)

        # Log extracted user ID
        print(f'Extracted user ID from token: {user_id_from_token}')

        # Construct the user data
        user_data = {
            'id': user_id_from_token,  # Use the user ID from the token
            'name': user.name,
            'username': user.username,
            'following': []  # Assuming you have a field for 'following'
        }

        # Log user data before saving
        print(f'User data to be saved: {user_data}')

        # Save the user data to the database
        db.collection('users').document(user_id_from_token).set(user_data)

        # Return the newly created user data
        return UserModel(**user_data)

    except Exception as e:
        # Handle any unexpected errors
        print(f'Error occurred while creating user: {e}')
        raise HTTPException(status_code=500, detail="Failed to create user: {}".format(str(e)))

# Route to get the profile of another user by user ID
# This registers the function get_user_profile as the handler for GET requests to "/user/{userID}"
# response_model specifies that the response should be validated against the User Model
@user_router.get("/user/{userID}", response_model=UserModel)
# Path describes how the user ID is a parameter, which is retrieved from the URL
async def get_user_profile(userID: str = Path(..., description="The ID of the user to retrieve")) -> UserModel:
    """
    Get the profile information of a user by their user ID.
    """
    # db.collection('users') accesses the users collection in the database
    # .document(userID) retrieves the document corresponding to the given userID
    user_ref = db.collection('users').document(userID)

    # This fetches the document from the database
    user_doc = user_ref.get()

    # if the document exists in the database or not
    if user_doc.exists:
        # convert the document to a dictionary
        user_data = user_doc.to_dict()

        # create and return a UserModel object using the extracted data
        return UserModel(
            id=user_data['id'],
            name=user_data['name'],
            username=user_data['username'],
            following=user_data['following']
        )
    else:
        # If the user does not exist, raise an HTTP 404 error
        raise HTTPException(status_code=404, detail="User not found")

# Route to get the profile of the current logged-in user
@user_router.get("/user/current", response_model=UserModel)
async def get_current_user(user_id: str = Depends(get_current_user_id)) -> UserModel:
    """
    Method to get the current user's information.
    """
    # get the document corresponding to the giver user ID from the database
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        # convert the document to a dictionary, then return the UserModel object with the data
        user_data = user_doc.to_dict()
        return UserModel(
            id=user_data['id'],
            name=user_data['name'],
            username=user_data['username'],
            following=user_data['following']
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Route to add another person to the user's following list
@user_router.post("/user/follow")
async def follow_user(follow_request: FollowRequest, user_id: str = Depends(get_current_user_id)):
    """
    Add the specified user ID to the current user's following list.
    """
    # Get the current user's document reference
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    # Handle the case that the user document does not exist
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the current user's data
    user_data = user_doc.to_dict()
    following = user_data.get('following', [])

    # Check if the user is already following the target user
    if follow_request.userIdToFollow in following:
        raise HTTPException(status_code=400, detail="Already following this user")

    # Add the target user ID to the following list
    following.append(follow_request.userIdToFollow)
    user_ref.update({'following': following})

    return {"message": "User followed successfully"}


# Endpoint to search users by username
@user_router.get("/search/users", response_model=List[UserModel])
async def search_users(
    username: str = Query(..., description="The username to search for"),
    limit: int = Query(10, description="Maximum number of results to return")
) -> List[UserModel]:
    """
    Endpoint to search for users by username.
    This performs a case-insensitive search and returns matching users.
    
    Args:
    - username (str): The username to search for.
    - limit (int): Maximum number of results to return (default: 10).

    Returns:
    - List[User]: A list of users matching the search query.
    """
    try:
        # Reference to the users collection in Firestore
        users_ref = db.collection('users')

        # Query to search for users by username (case-insensitive search) and limit the results
        query = users_ref.where('username', '>=', username).where('username', '<=', username + '\uf8ff').limit(limit)

        # Retrieve documents that match the search
        docs = query.stream()

        # List to hold the search results
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user = UserModel(
                id=user_data['id'],
                name=user_data['name'],
                username=user_data['username'],
                following=user_data.get('following', [])
            )
            users.append(user)

        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
