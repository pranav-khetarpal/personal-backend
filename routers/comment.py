from datetime import datetime
import pytz
from fastapi import HTTPException, APIRouter, Depends, status
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
        user_comments_on_post = list(post_ref.collection('comments').where('userId', '==', user_id).stream())

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
