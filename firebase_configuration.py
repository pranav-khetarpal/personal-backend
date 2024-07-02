# import firebase_admin
# from firebase_admin import credentials, firestore

# def initialize_firebase():
#     """
#     Initializes the Firebase Admin SDK and returns the Firestore client.
#     """

#     # Initialize Firebase Admin SDK with the service account key JSON file
#     cred = credentials.Certificate("C:\GitHub\personal-backend\personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json")
#     firebase_admin.initialize_app(cred)

#     # Return the Firestore client, which is an instance of the database
#     return firestore.client()


# # Initialize the Firebase app, which only needs to be done once per time the backend is run
# db = initialize_firebase()




# import os
# from firebase_admin import credentials, firestore, initialize_app

# def initialize_firebase():
#     # Get the Firebase credentials from an environment variable
#     cred_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
#     if not cred_json:
#         raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set")

#     # Load the credentials from the JSON string
#     cred = credentials.Certificate(cred_json)
#     initialize_app(cred)
#     return firestore.client()

# db = initialize_firebase()




import os
from firebase_admin import credentials, firestore, initialize_app

def initialize_firebase():
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not cred_path:
        raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
    
    cred = credentials.Certificate(cred_path)
    firebase_app = initialize_app(cred)
    return firestore.client()

# Initialize Firebase when the module is imported
db = initialize_firebase()
