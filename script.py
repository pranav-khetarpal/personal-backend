import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Add the user's own ID to their existing following list
users_ref = db.collection('users')
docs = users_ref.stream()

for doc in docs:
    user_id = doc.id
    user_ref = users_ref.document(user_id)

    # Get the current following list
    user_data = user_ref.get().to_dict()
    current_following = user_data.get('following', [])

    # Append the user's own ID to the following list
    if user_id not in current_following:
        current_following.append(user_id)

    # Update the document with the modified following list
    user_ref.update({'following': current_following})
    