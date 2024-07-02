from datetime import datetime
from typing import List, Optional
import pytz
from fastapi import HTTPException, APIRouter, Depends, Query, status
from models.comment_models import CommentModel, CreateCommentModel
from routers.user_interactions import get_current_user_id
from firebase_configuration import db
from firebase_admin import firestore

# Create a router for the comment-related requests
comment_router = APIRouter()

@comment_router.post("/comments/create", response_model=CommentModel)
async def create_comment(comment: CreateCommentModel, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to create a new comment
    """
    post_ref = db.collection('posts').document(comment.postId)
    comment_id = post_ref.collection('comments').document().id
    comment_data = {
        'id': comment_id,
        'userId': user_id,
        'content': comment.content,
        'timestamp': datetime.now(pytz.UTC),
        'likes_count': 1,
    }

    try:
        # Save the comment to Firestore under the post's comments subcollection
        post_ref.collection('comments').document(comment_id).set(comment_data)

        # Initialize the likes sub-collection with the user ID of the comment creator
        likes_ref = post_ref.collection('comments').document(comment_id).collection('likes')
        likes_ref.document(user_id).set({'liked_at': firestore.SERVER_TIMESTAMP})

        # Increment the comment count in the post document
        post_ref.update({'comments_count': firestore.Increment(1)})

        # Add the post to the user's commentedPosts subcollection
        user_ref = db.collection('users').document(user_id)
        commented_posts_ref = user_ref.collection('commentedPosts').document(comment.postId)
        commented_posts_ref.set({'commented_at': firestore.SERVER_TIMESTAMP})

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create comment: {e}",
        )

    # return a comment model, while ensuring that the current user likes their own comment
    return CommentModel(**comment_data, isLikedByUser=True)


@comment_router.delete("/comments/delete/{post_id}/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(post_id: str, comment_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint to delete a comment
    """
    post_ref = db.collection('posts').document(post_id)
    comment_ref = post_ref.collection('comments').document(comment_id)

    # Check if the comment exists and belongs to the current user
    comment = comment_ref.get()
    if not comment.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment_data = comment.to_dict()
    if comment_data['userId'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment"
        )

    try:
        # Start a Firestore batch
        batch = db.batch()

        # Delete comment's likes and remove from users' likedComments subcollections
        likes_ref = comment_ref.collection('likes')
        likes = likes_ref.stream()
        for like in likes:
            user_ref = db.collection('users').document(like.id)
            liked_comment_ref = user_ref.collection('likedComments').document(comment_id)
            batch.delete(liked_comment_ref)
            batch.delete(like.reference)

        # Delete the comment document
        batch.delete(comment_ref)

        # Commit the deletion of the comment and its likes
        batch.commit()

        # Decrement the comment count in the post document
        post_ref.update({'comments_count': firestore.Increment(-1)})

        # Check if the user has any other comments on the same post
        user_comments_on_post = List(post_ref.collection('comments').where('userId', '==', user_id).stream())

        if not any(user_comments_on_post):
            # If no other comments by the user, remove the post from the user's commentedPosts subcollection
            user_ref = db.collection('users').document(user_id)
            commented_posts_ref = user_ref.collection('commentedPosts').document(post_id)
            batch.delete(commented_posts_ref)

        # Commit the batch after checking user's comments on post
        batch.commit()

        return {"message": "Comment deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {e}",
        )


@comment_router.get("/comments/fetch", response_model=List[CommentModel])
async def fetch_comments(
    post_id: str,
    limit: int = Query(10, description="Limit the number of comments returned"),
    start_after: Optional[str] = Query(None, description="Start after this comment ID"),
    user_id: str = Depends(get_current_user_id),
) -> List[CommentModel]:
    """
    Endpoint to fetch comments for a given post with pagination
    """
    try:
        post_ref = db.collection('posts').document(post_id)
        comments_query = post_ref.collection('comments').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)

        if start_after:
            start_after_doc = post_ref.collection('comments').document(start_after).get()
            if start_after_doc.exists:
                comments_query = comments_query.start_after(start_after_doc)
            else:
                raise HTTPException(status_code=404, detail="Start after comment not found")

        comments_docs = comments_query.stream()
        comments = []

        for comment in comments_docs:
            comment_data = comment.to_dict()
            is_liked = post_ref.collection('comments').document(comment.id).collection('likes').document(user_id).get().exists
            comments.append(CommentModel(
                id=comment.id,
                postId=post_id,
                userId=comment_data['userId'],
                content=comment_data['content'],
                timestamp=comment_data['timestamp'],
                likes_count=comment_data.get('likes_count', 0),
                isLikedByUser=is_liked,
            ))

        return comments

    except Exception as e:
        print(f"An error occurred while fetching comments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

def increment_comment_likes(post_ref, comment_id, user_id):
    try:
        comment_ref = post_ref.collection('comments').document(comment_id)
        comment_snapshot = comment_ref.get()
        if not comment_snapshot.exists:
            raise HTTPException(status_code=404, detail="Comment not found")

        likes_count = comment_snapshot.get('likes_count') + 1
        comment_ref.update({'likes_count': likes_count})

        likes_ref = comment_ref.collection('likes').document(user_id)
        likes_ref.set({'liked_at': datetime.now()})

        user_liked_comments_ref = db.collection('users').document(user_id).collection('likedComments').document(comment_ref.id)
        user_liked_comments_ref.set({'liked_at': datetime.now()})

        print("Comment likes incremented successfully")

    except Exception as e:
        print(f"Failed to increment comment likes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to increment comment likes: {e}")


@comment_router.post("/comments/like/{post_id}/{comment_id}", status_code=status.HTTP_200_OK)
async def like_comment(post_id: str, comment_id: str, user_id: str = Depends(get_current_user_id)):
    post_ref = db.collection('posts').document(post_id)

    likes_ref = post_ref.collection('comments').document(comment_id).collection('likes').document(user_id)
    if likes_ref.get().exists:
        raise HTTPException(status_code=400, detail="Comment already liked by user")

    try:
        increment_comment_likes(post_ref, comment_id, user_id)
    except Exception as e:
        print(f"Failed to like comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to like comment: {e}")

    return {"message": "Comment liked successfully"}


def decrement_comment_likes(post_ref, comment_id, user_id):
    try:
        comment_ref = post_ref.collection('comments').document(comment_id)
        comment_snapshot = comment_ref.get()
        if not comment_snapshot.exists:
            raise HTTPException(status_code=404, detail="Comment not found")

        likes_count = comment_snapshot.get('likes_count') - 1
        if likes_count < 0:
            likes_count = 0
        comment_ref.update({'likes_count': likes_count})

        likes_ref = comment_ref.collection('likes').document(user_id)
        likes_ref.delete()

        user_liked_comments_ref = db.collection('users').document(user_id).collection('likedComments').document(comment_ref.id)
        user_liked_comments_ref.delete()

        print("Comment likes decremented successfully")

    except Exception as e:
        print(f"Failed to decrement comment likes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to decrement comment likes: {e}")


@comment_router.post("/comments/unlike/{post_id}/{comment_id}", status_code=status.HTTP_200_OK)
async def unlike_comment(post_id: str, comment_id: str, user_id: str = Depends(get_current_user_id)):
    post_ref = db.collection('posts').document(post_id)

    likes_ref = post_ref.collection('comments').document(comment_id).collection('likes').document(user_id)
    if not likes_ref.get().exists:
        raise HTTPException(status_code=400, detail="Comment not liked by user")

    try:
        decrement_comment_likes(post_ref, comment_id, user_id)
    except Exception as e:
        print(f"Failed to unlike comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unlike comment: {e}")

    return {"message": "Comment unliked successfully"}
