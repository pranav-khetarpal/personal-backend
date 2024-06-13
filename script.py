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

# Initialize Firebase Admin SDK
cred = credentials.Certificate('personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Reference to the users collection
users_ref = db.collection('users')

# URL with the token
default_image_url_with_token = 'https://firebasestorage.googleapis.com/v0/b/personal-app-fe948.appspot.com/o/profile_images%2Fdefault_profile_image.jpg?alt=media&token=f33a9720-2010-41b4-a6d0-4ba450db2f99'

def update_user_documents():
    users = users_ref.stream()
    for user in users:
        user_ref = users_ref.document(user.id)
        user_ref.update({'profile_image_url': default_image_url_with_token})
        print(f'Updated user {user.id} with default profile image URL.')

update_user_documents()
