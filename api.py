from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_configuration import initialize_firebase
from routers.user import user_router
from routers.post import post_router

#
# This is a class to simply create our app instance and add the routers to it
#

# Create FastAPI instance
app = FastAPI()

# # List of origins that are allowed to make requests
# origins = [
#     "http://localhost",
#     "http://localhost:8000",
#     "http://10.0.0.32",
#     "http://10.0.0.32:8000",
#     # "http://localhost:50090",
# ]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers, which allow us to modularize our code among different files
app.include_router(user_router)
app.include_router(post_router)