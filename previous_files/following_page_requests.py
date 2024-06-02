# from fastapi import HTTPException, APIRouter, Depends, Query
# from add_post_requests import get_current_user_id

# from firebase_configuration import db
# from models.post_model import Post
# from models.user_model import User
# from typing import List, Optional

# # Initialize the Firebase app
# db = initialize_firebase()

# # Create a router for the user information requests
# user_router = APIRouter()

# Create a router for the post information requests
# post_router = APIRouter()

# # Helper function to get current user ID from token
# def get_current_user_id(token: str = Header(...)) -> str:
#     try:
#         decoded_token = auth.verify_id_token(token)
#         return decoded_token['uid']
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")

# # Define routes for user operations
# @user_router.get("/current", response_model=User)
# async def get_current_user(user_id: str = Depends(get_current_user_id)) -> User:
#     """
#     Method to get the current user's information
#     """
#     user_ref = db.collection('users').document(user_id)
#     user_doc = user_ref.get()
    
#     if user_doc.exists:
#         user_data = user_doc.to_dict()
#         return User(id=user_data['id'], 
#                     name=user_data['name'], 
#                     username=user_data['username'], 
#                     following=user_data['following']
#                     )
#     else:
#         raise HTTPException(status_code=404, detail="User not found")

# # Define routes for post operations with pagination
# @post_router.get("/", response_model=List[Post])
# async def get_posts(user_id: str = Depends(get_current_user_id), 
#                     limit: int = Query(10, description="Limit the number of posts returned"), 
#                     start_after: Optional[str] = Query(None, description="Start after this post ID")) -> List[Post]:
#     """
#     Method to return posts for the current user's following list with pagination
#     """
#     # Fetch the current user's data
#     user_ref = db.collection('users').document(user_id)
#     user_doc = user_ref.get()
    
#     if not user_doc.exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     user_data = user_doc.to_dict()
#     following = user_data['following']

#     # Fetch posts from users that the current user is following with pagination
#     posts_query = db.collection('posts').where('userId', 'in', following).order_by('timestamp').limit(limit)
    
#     # If start_after is provided, add it to the query
#     if start_after:
#         start_after_doc = db.collection('posts').document(start_after).get()
#         if start_after_doc.exists:
#             posts_query = posts_query.start_after(start_after_doc)
#         else:
#             raise HTTPException(status_code=404, detail="Start after post not found")

#     posts_docs = posts_query.stream()
    
#     posts = []
#     for post in posts_docs:
#         post_data = post.to_dict()
#         posts.append(Post(id=post_data['id'], 
#                           userId=post_data['userId'], 
#                           content=post_data['content'], 
#                           timestamp=post_data['timestamp']
#                         ))
#     return posts
