# import firebase_admin
# from firebase_admin import credentials, firestore

# cred = credentials.Certificate('personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json')
# firebase_admin.initialize_app(cred)

# db = firestore.client()

# # Add the user's own ID to their existing following list
# users_ref = db.collection('users')
# docs = users_ref.stream()

# for doc in docs:
#     user_id = doc.id
#     user_ref = users_ref.document(user_id)

#     # Get the current following list
#     user_data = user_ref.get().to_dict()
#     current_following = user_data.get('following', [])

#     # Append the user's own ID to the following list
#     if user_id not in current_following:
#         current_following.append(user_id)

#     # Update the document with the modified following list
#     user_ref.update({'following': current_following})

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Reference to the posts collection
posts_ref = db.collection('posts')

# Function to update posts with likes_count
def update_posts_with_likes_count():
    # Get all documents in the posts collection
    posts = posts_ref.stream()

    for post in posts:
        post_ref = posts_ref.document(post.id)
        post_data = post.to_dict()
        
        # Check if 'likes_count' field exists
        if 'likes_count' not in post_data:
            # Update the document with likes_count field set to 1
            post_ref.update({'likes_count': 1})
            print(f"Updated post {post.id} with likes_count = 1")
        else:
            print(f"Post {post.id} already has likes_count")

if __name__ == "__main__":
    update_posts_with_likes_count()
