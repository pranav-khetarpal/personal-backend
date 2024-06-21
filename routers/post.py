from datetime import datetime
import pytz
from fastapi import HTTPException, APIRouter, Depends, Query, status
from routers.user_interactions import get_current_user_id
from firebase_configuration import db
from firebase_admin import firestore
from models.post_models import PostModel, CreatePostModel
from typing import List, Optional

# Create a router for the post-related requests
post_router = APIRouter()

@post_router.post("/posts/create", response_model=PostModel)
async def create_post(post: CreatePostModel, user_id: str = Depends(get_current_user_id)) -> PostModel:
    """
    Endpoint to create a new post
    """
    post_id = db.collection('posts').document().id
    post_data = {
        'id': post_id,
        'userId': user_id,
        'content': post.content,
        'timestamp': datetime.now(pytz.UTC),  # Ensure UTC timezone is used
        'likes_count': 1,  # Initialize the likes count to 1
        'comments_count': 0,  # Initialize the comments count to 0
    }

    try:
        # Save the post to Firestore
        db.collection('posts').document(post_id).set(post_data)

        # Initialize the likes sub-collection with the user ID of the post creator
        likes_ref = db.collection('posts').document(post_id).collection('likes')
        likes_ref.document(user_id).set({'liked_at': firestore.SERVER_TIMESTAMP})

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create post: {e}",
        )
    
    # return a post model, while ensuring that the current user likes their own post
    return PostModel(**post_data, isLikedByUser=True)


@post_router.delete("/posts/delete/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to delete a post
    """
    post_ref = db.collection('posts').document(post_id)

    # Check if the post exists and belongs to the current user
    post = post_ref.get()
    if not post.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post_data = post.to_dict()
    if post_data['userId'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post"
        )

    try:
        # Start a Firestore batch
        batch = db.batch()

        # Delete post's likes and remove from users' likedPosts subcollections
        likes_ref = post_ref.collection('likes')
        likes = likes_ref.stream()
        for like in likes:
            user_ref = db.collection('users').document(like.id)
            liked_post_ref = user_ref.collection('likedPosts').document(post_id)
            batch.delete(liked_post_ref)
            batch.delete(like.reference)

        # Delete post's comments and their likes, and remove from users' commentedPosts subcollections
        comments_ref = post_ref.collection('comments')
        comments = comments_ref.stream()
        for comment in comments:
            comment_ref = comment.reference
            comment_data = comment.to_dict()

            # Delete comment's likes and remove from users' likedComments subcollections
            comment_likes_ref = comment_ref.collection('likes')
            comment_likes = comment_likes_ref.stream()
            for comment_like in comment_likes:
                user_ref = db.collection('users').document(comment_like.id)
                liked_comment_ref = user_ref.collection('likedComments').document(comment_ref.id)
                batch.delete(liked_comment_ref)
                batch.delete(comment_like.reference)

            # Remove the post from the user's commentedPosts subcollection
            user_ref = db.collection('users').document(comment_data['userId'])
            commented_post_ref = user_ref.collection('commentedPosts').document(post_id)
            batch.delete(commented_post_ref)

            # Delete the comment document
            batch.delete(comment_ref)

        # Delete the post document
        batch.delete(post_ref)

        # Commit the batch
        batch.commit()

        return {"message": "Post deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {e}",
        )


@post_router.get("/posts/fetch", response_model=List[PostModel])
async def get_posts(user_id: str = Depends(get_current_user_id), 
                    limit: int = Query(10, description="Limit the number of posts returned"), 
                    start_after: Optional[str] = Query(None, description="Start after this post ID")) -> List[PostModel]:
    """
    Method to return posts for the current user's following list with pagination
    """
    print("Request received at /posts/fetch")
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
            is_liked = db.collection('posts').document(post.id).collection('likes').document(user_id).get().exists
            posts.append(PostModel(
                id=post.id, 
                userId=post_data['userId'], 
                content=post_data['content'], 
                timestamp=post_data['timestamp'],
                likes_count=post_data.get('likes_count', 0),
                comments_count=post_data.get('comments_count', 0),  # Add comments_count
                isLikedByUser=is_liked
            ))
        return posts

    except Exception as e:
        # Handle any unexpected errors and return an appropriate response
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@post_router.get("/posts/user", response_model=List[PostModel])
async def get_user_posts(
    user_id: str = Query(..., description="ID of the user whose posts to fetch"),
    limit: int = Query(10, description="Limit the number of posts returned"), 
    start_after: Optional[str] = Query(None, description="Start after this post ID"),
    current_user_id: str = Depends(get_current_user_id)
) -> List[PostModel]:
    """
    Method to return posts for a specific user with pagination
    """
    print("Request received at /posts/user")
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
            is_liked = db.collection('posts').document(post.id).collection('likes').document(current_user_id).get().exists
            posts.append(PostModel(
                id=post.id, 
                userId=post_data['userId'], 
                content=post_data['content'], 
                timestamp=post_data['timestamp'],
                likes_count=post_data.get('likes_count', 0),
                comments_count=post_data.get('comments_count', 0),  # Add comments_count
                isLikedByUser=is_liked
            ))
        return posts

    except Exception as e:
        # Handle any unexpected errors and return an appropriate response
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def increment_likes(post_ref, user_id):
    """
    Helper function to increment likes and add like document
    """
    try:
        # Update the likes count of the post
        post_snapshot = post_ref.get()
        likes_count = post_snapshot.get('likes_count') + 1
        post_ref.update({'likes_count': likes_count})

        # Add the like by creating a document in the likes subcollection
        likes_ref = post_ref.collection('likes').document(user_id)
        likes_ref.set({'liked_at': datetime.now()})

        # Add the post to the user's liked posts subcollection
        user_liked_posts_ref = db.collection('users').document(user_id).collection('likedPosts').document(post_ref.id)
        user_liked_posts_ref.set({'liked_at': datetime.now()})

        print("Likes incremented successfully")

    except Exception as e:
        print(f"Failed to increment likes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to increment likes: {e}")

@post_router.post("/posts/like/{post_id}", status_code=status.HTTP_200_OK)
async def like_post(post_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to like a post
    """
    post_ref = db.collection('posts').document(post_id)
    post_snapshot = post_ref.get()

    if not post_snapshot.exists:
        raise HTTPException(status_code=404, detail="Post not found")

    likes_ref = post_ref.collection('likes').document(user_id)
    if likes_ref.get().exists:
        raise HTTPException(status_code=400, detail="Post already liked by user")

    try:
        # Increment the likes count and add the like
        increment_likes(post_ref, user_id)
        
    except Exception as e:
        # Log the exception for debugging
        print(f"Failed to like post: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to like post: {e}")

    return {"message": "Post liked successfully"}

def decrement_likes(post_ref, user_id):
    """
    Helper function to decrement likes and delete like document
    """
    try:
        # Update the likes count of the post
        post_snapshot = post_ref.get()
        likes_count = post_snapshot.get('likes_count') - 1
        if likes_count < 0:
            likes_count = 0  # Ensure likes_count doesn't go negative
        post_ref.update({'likes_count': likes_count})

        # Remove the like document from the likes subcollection
        likes_ref = post_ref.collection('likes').document(user_id)
        likes_ref.delete()

        # Remove the post from the user's liked posts subcollection
        user_liked_posts_ref = db.collection('users').document(user_id).collection('likedPosts').document(post_ref.id)
        user_liked_posts_ref.delete()
        
        print("Likes decremented successfully")

    except Exception as e:
        print(f"Failed to decrement likes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to decrement likes: {e}")

@post_router.post("/posts/unlike/{post_id}", status_code=status.HTTP_200_OK)
async def unlike_post(post_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to unlike a post
    """
    post_ref = db.collection('posts').document(post_id)
    post_snapshot = post_ref.get()

    if not post_snapshot.exists:
        raise HTTPException(status_code=404, detail="Post not found")

    likes_ref = post_ref.collection('likes').document(user_id)
    if not likes_ref.get().exists:
        raise HTTPException(status_code=400, detail="Post not liked by user")

    try:
        # Decrement the likes count and remove the like
        decrement_likes(post_ref, user_id)
        
    except Exception as e:
        # Log the exception for debugging
        print(f"Failed to unlike post: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unlike post: {e}")

    return {"message": "Post unliked successfully"}
