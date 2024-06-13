from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel
from routers.user_interactions import get_current_user_id

# Create a router for the profile image related requests
profile_image_router = APIRouter()


class UpdateProfileImageModel(BaseModel):
    profile_image_url: str

@profile_image_router.put("/user/updateProfileImage")
async def update_profile_image(
    update_data: UpdateProfileImageModel,
    user_id: str = Depends(get_current_user_id)
):
    """
    Endpoint to update a user's profile image
    """
    try:
        user_ref = firestore.client().collection('users').document(user_id)
        user_ref.update({'profile_image_url': update_data.profile_image_url})
        
        return {"message": "Profile image updated successfully"}
    except Exception as e:
        print(f'Error occurred while updating profile image: {e}')
        raise HTTPException(status_code=500, detail="Failed to update profile image")
    