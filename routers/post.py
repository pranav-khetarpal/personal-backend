from datetime import datetime
import pytz
from fastapi import HTTPException, APIRouter, Depends, Query, status, Request
from models.create_post_model import CreatePostModel
from routers.user_interactions import get_current_user_id

from firebase_configuration import db
from firebase_admin import firestore
from models.post_model import PostModel
from typing import List, Optional

# Create a router for the post related requests
post_router = APIRouter()

@post_router.post("/posts/create", response_model=PostModel)
async def create_post(post: CreatePostModel, user_id: str = Depends(get_current_user_id)) -> PostModel:
    """
    Endpoint to create a new post
    """

    # get the postID corresponding to the new post document from the database
    post_id = db.collection('posts').document().id
    post_data = {
        'id': post_id,
        'userId': user_id,
        'content': post.content,
        'timestamp': datetime.now(pytz.UTC)  # Ensure UTC timezone is used
    }

    try:
        # Save the post to Firestore
        db.collection('posts').document(post_id).set(post_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {e}",
        )

    return PostModel(**post_data)
    
@post_router.get("/posts/fetch", response_model=List[PostModel])
async def get_posts(user_id: str = Depends(get_current_user_id), 
                    limit: int = Query(10, description="Limit the number of posts returned"), 
                    start_after: Optional[str] = Query(None, description="Start after this post ID")) -> List[PostModel]:
    """
    Method to return posts for the current user's following list with pagination
    """
    print("Request received at /posts/fetch")  # Add this line
    try:
        # Fetch the current user's data
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        # Handle the case that no user data exists
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Convert the user's document to a dictionary
        user_data = user_doc.to_dict()

        # Retrieve the list of users that the current user is following
        following = user_data.get('following', [])

        # Check if following list is empty
        if not following:
            return []

        # Fetch posts from users that the current user is following with pagination
        posts_query = db.collection('posts').where('userId', 'in', following).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)

        # If start_after is provided, add it to the query
        if start_after:
            start_after_doc = db.collection('posts').document(start_after).get()
            if start_after_doc.exists:
                posts_query = posts_query.start_after(start_after_doc)
            else:
                raise HTTPException(status_code=404, detail="Start after post not found")

        posts_docs = posts_query.stream()
        posts = []

        # Convert each post document to a PostModel object and add it to the list of posts
        for post in posts_docs:
            post_data = post.to_dict()
            posts.append(PostModel(id=post_data['id'], 
                                   userId=post_data['userId'], 
                                   content=post_data['content'], 
                                   timestamp=post_data['timestamp']))
        return posts

    except Exception as e:
        # Handle any unexpected errors and return an appropriate response
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@post_router.get("/posts/user", response_model=List[PostModel])
async def get_user_posts(
    user_id: str = Query(..., description="ID of the user whose posts to fetch"),
    limit: int = Query(10, description="Limit the number of posts returned"), 
    start_after: Optional[str] = Query(None, description="Start after this post ID")
) -> List[PostModel]:
    """
    Method to return posts for a specific user with pagination
    """
    print("Request received at /posts/user")  # Add this line
    try:
        # Fetch the specified user's data
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        # Handle the case that the user does not exist
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch posts for the specified user with pagination
        posts_query = db.collection('posts').where('userId', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)

        # If start_after is provided, add it to the query
        if start_after:
            start_after_doc = db.collection('posts').document(start_after).get()
            if start_after_doc.exists:
                posts_query = posts_query.start_after(start_after_doc)
            else:
                raise HTTPException(status_code=404, detail="Start after post not found")

        posts_docs = posts_query.stream()
        posts = []

        # Convert each post document to a PostModel object and add it to the list of posts
        for post in posts_docs:
            post_data = post.to_dict()
            posts.append(PostModel(id=post.id, 
                                   userId=post_data['userId'], 
                                   content=post_data['content'], 
                                   timestamp=post_data['timestamp']))
        return posts

    except Exception as e:
        # Handle any unexpected errors and return an appropriate response
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

