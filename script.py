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

db = firestore.client()

# Define the initial stock list
initial_stock_list = {
    'name': 'First List',
    'tickers': ['AAPL', 'MSFT', 'TSLA', 'AMZN', 'NVDA']
}

# Add the stockLists subcollection to each user document and initialize with the initial stock list
users_ref = db.collection('users')
docs = users_ref.stream()

for doc in docs:
    user_id = doc.id
    user_ref = users_ref.document(user_id)

    # Check if stockLists subcollection already exists for the user
    stock_lists_ref = user_ref.collection('stockLists')
    stock_lists_docs = stock_lists_ref.stream()

    # If there are no existing stock lists, add the initial stock list
    if stock_lists_docs is None:
        print(f"StockLists subcollection already exists for user {user_id}. Skipping initialization.")
    else:
        # Initialize stockLists subcollection with initial stock list
        stock_list_doc_ref = stock_lists_ref.document()
        stock_list_doc_ref.set(initial_stock_list)
        print(f"Initialized stockLists subcollection for user {user_id} with initial stock list.")

print("Initialization complete.")
