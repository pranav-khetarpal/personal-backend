import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK and returns the Firestore client.
    """

    # Initialize Firebase Admin SDK with the service account key JSON file
    cred = credentials.Certificate("C:\GitHub\personal-backend\personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json")
    firebase_admin.initialize_app(cred)

    # Return the Firestore client, which is an instance of the database
    return firestore.client()


# Initialize the Firebase app, which only needs to be done once per time the backend is run
db = initialize_firebase()
