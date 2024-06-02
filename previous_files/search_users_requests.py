# from fastapi import FastAPI, HTTPException, APIRouter
# from firebase_admin import firestore
# from typing import List
# from firebase_configuration import initialize_firebase

# from firebase_configuration import db
# from models.user_model import User

# # # Initialize the Firebase app
# # db = initialize_firebase()

# # Define the router for search users
# search_users_router = APIRouter()

# # Endpoint to search users by username
# @search_users_router.get("/api/search/users", response_model=List[User])
# async def search_users(username: str):
#     """
#     Endpoint to search for users by username.
#     This performs a case-insensitive search and returns matching users.
    
#     Args:
#     - username (str): The username to search for.

#     Returns:
#     - List[User]: A list of users matching the search query.
#     """
#     try:
#         # Reference to the users collection in Firestore
#         users_ref = db.collection('users')

#         # Query to search for users by username (case-insensitive search)
#         query = users_ref.where('username', '>=', username).where('username', '<=', username + '\uf8ff')
#         docs = query.stream()

#         # List to hold the search results
#         users = []
#         for doc in docs:
#             user_data = doc.to_dict()
#             user = User(
#                 id=user_data['id'],
#                 name=user_data['name'],
#                 username=user_data['username'],
#                 following=user_data.get('following', [])
#             )
#             users.append(user)

#         return users

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
