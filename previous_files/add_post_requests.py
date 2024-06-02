# from fastapi import FastAPI, HTTPException, APIRouter, Depends, Header
# from pydantic import BaseModel
# from datetime import datetime
# from firebase_admin import auth, firestore

# from firebase_configuration import db
# from models.post_model import Post

# # # Initialize the Firebase app
# # db = initialize_firebase()

# # Create a router for the add post requests
# add_post_router = APIRouter()

# @add_post_router.post("/add_post", response_model=Post)
# async def create_post(post: Post, user_id: str = Depends(get_current_user_id)) -> Post:
#     """
#     Endpoint to create a new post
#     """
#     post_id = db.collection('posts').document().id
#     post_data = {
#         'id': post_id,
#         'userId': user_id,
#         'content': post.content,
#         'timestamp': datetime.now(datetime.UTC)
#     }

#     # Save the post to Firestore
#     db.collection('posts').document(post_id).set(post_data)

#     return Post(**post_data)
