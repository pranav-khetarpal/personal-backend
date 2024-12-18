from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, Path, Query
from firebase_admin import auth, firestore
import re
from firebase_configuration import db
from models.following_models import FollowRequest, UnfollowRequest
from models.user_models import UserModel, CreateUserModel

# Create a router for the user interactions related requests
user_interactions_router = APIRouter()

def get_current_user_id(authorization: str = Header(...)) -> str:
    """
    Helper function to get current user ID from token
    """
    try:

        # Remove all whitespace characters
        cleaned_authorization = re.sub(r'\s+', '', authorization)

        # Extract the token part, excluding "Bearer"
        token = re.sub(r'Bearer', '', cleaned_authorization)
        
        # decodes the token and verifies it
        decoded_token = auth.verify_id_token(token)

        # Returns the user ID (uid) if the token is valid
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@user_interactions_router.get("/user/current", response_model=UserModel)
async def get_current_user(user_id: str = Depends(get_current_user_id)) -> UserModel:
    """
    Endpoint to retrieve the profile information of the current user.
    """
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        user_data = user_doc.to_dict()

        # Initialize stockLists dictionary
        stockLists = {}

        # Fetch stock lists from the subcollection
        stock_lists_ref = user_ref.collection('stockLists')
        stock_lists_docs = stock_lists_ref.stream()

        for doc in stock_lists_docs:
            stock_list_data = doc.to_dict()
            list_name = stock_list_data.get('name')
            tickers = stock_list_data.get('tickers', [])
            if list_name:
                stockLists[list_name] = tickers

        # Add stockLists to user_data
        user_data['stockLists'] = stockLists

        return UserModel(**user_data)
    else:
        raise HTTPException(status_code=404, detail="User not found")


# This registers the function get_user_profile as the handler for GET requests to "/user/{userID}"
# response_model specifies that the response should be validated against the User Model
@user_interactions_router.get("/user/{userID}", response_model=UserModel)
# Path describes how the user ID is a parameter, which is retrieved from the URL
async def get_user_profile(userID: str = Path(..., description="The ID of the user to retrieve")) -> UserModel:
    """
    Endpoint to get the profile information of a user by their user ID.
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
        return UserModel(**user_data)
    else:
        # If the user does not exist, raise an HTTP 404 error
        raise HTTPException(status_code=404, detail="User not found")


# @user_interactions_router.post("/user/follow")
# async def follow_user(follow_request: FollowRequest, user_id: str = Depends(get_current_user_id)):
#     """
#     Endpoint to add the specified user ID to the current user's following list.
#     """
#     # Get the current user's document reference
#     user_ref = db.collection('users').document(user_id)
#     user_doc = user_ref.get()

#     # Handle the case that the user document does not exist
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

@user_interactions_router.post("/user/follow")
async def follow_user(follow_request: FollowRequest, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to add the specified user ID to the current user's following list.
    """
    # Get the current user's document reference
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the target user's document reference
    target_user_ref = db.collection('users').document(follow_request.userIdToFollow)
    target_user_doc = target_user_ref.get()

    if not target_user_doc.exists:
        raise HTTPException(status_code=404, detail="Target user not found")

    # Check if already following
    following_ref = user_ref.collection('following').document(follow_request.userIdToFollow)
    if following_ref.get().exists:
        raise HTTPException(status_code=400, detail="Already following this user")

    # Add target user to following subcollection
    following_ref.set({})

    # Increment following count for current user
    user_ref.update({'following_count': firestore.Increment(1)})

    # Add current user to target user's followers subcollection
    target_user_ref.collection('followers').document(user_id).set({})

    # Increment followers count for target user
    target_user_ref.update({'followers_count': firestore.Increment(1)})

    return {"message": "User followed successfully"}



# @user_interactions_router.post("/user/unfollow")
# async def unfollow_user(unfollow_request: UnfollowRequest, user_id: str = Depends(get_current_user_id)):
#     """
#     Remove the specified user ID from the current user's following list.
#     """
#     # Get the current user's document reference
#     user_ref = db.collection('users').document(user_id)
#     user_doc = user_ref.get()

#     # Handle the case that the user document does not exist
#     if not user_doc.exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Get the current user's data
#     user_data = user_doc.to_dict()
#     following = user_data.get('following', [])

#     # Check if the user is not following the target user
#     if unfollow_request.userIdToUnfollow not in following:
#         raise HTTPException(status_code=400, detail="Not following this user")

#     # Remove the target user ID from the following list
#     following.remove(unfollow_request.userIdToUnfollow)
#     user_ref.update({'following': following})

#     return {"message": "User unfollowed successfully"}

@user_interactions_router.post("/user/unfollow")
async def unfollow_user(unfollow_request: UnfollowRequest, user_id: str = Depends(get_current_user_id)):
    """
    Remove the specified user ID from the current user's following list.
    """
    # Get the current user's document reference
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the target user's document reference
    target_user_ref = db.collection('users').document(unfollow_request.userIdToUnfollow)
    target_user_doc = target_user_ref.get()

    if not target_user_doc.exists:
        raise HTTPException(status_code=404, detail="Target user not found")

    # Check if not following
    following_ref = user_ref.collection('following').document(unfollow_request.userIdToUnfollow)
    if not following_ref.get().exists:
        raise HTTPException(status_code=400, detail="Not following this user")

    # Remove target user from following subcollection
    following_ref.delete()

    # Decrement following count for current user
    user_ref.update({'following_count': firestore.Increment(-1)})

    # Remove current user from target user's followers subcollection
    target_user_ref.collection('followers').document(user_id).delete()

    # Decrement followers count for target user
    target_user_ref.update({'followers_count': firestore.Increment(-1)})

    return {"message": "User unfollowed successfully"}


@user_interactions_router.get("/search/users", response_model=List[UserModel])
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
            
            # Remove 'stockLists' if it is not needed
            user_data.pop('stockLists', None)

            user = UserModel(**user_data)
            users.append(user)

        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@user_interactions_router.get("/user/is_following/{target_user_id}", response_model=bool)
async def is_following_user(target_user_id: str, user_id: str = Depends(get_current_user_id)) -> bool:
    """
    Check if the current user is following the target user.
    """
    try:
        # Reference to the subcollection of the current user's 'following' list
        following_ref = db.collection('users').document(user_id).collection('following').document(target_user_id)
        following_doc = following_ref.get()

        # Return true if the document exists (current user is following target user)
        return following_doc.exists

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
