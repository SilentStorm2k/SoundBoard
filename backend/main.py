from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import MongoDBUserDatabase
import boto3
from bson import ObjectId

# Configuration
DATABASE_URL = "mongodb://localhost:27017"
SECRET = "YOUR_SECRET_KEY"  # Replace with a secure secret key
S3_BUCKET_NAME = "your-s3-bucket-name"  # Replace with your S3 bucket name

# FastAPI app setup
app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = AsyncIOMotorClient(DATABASE_URL)
db = client["soundboard"]

# User model
class User(models.BaseUser):
    pass

class UserCreate(models.BaseUserCreate):
    pass

class UserUpdate(models.BaseUserUpdate):
    pass

class UserDB(User, models.BaseUserDB):
    pass

# JWT Authentication setup
auth_backends = [
    JWTAuthentication(secret=SECRET, lifetime_seconds=3600),
]

# FastAPI Users setup
user_db = MongoDBUserDatabase(UserDB, db["users"])
fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

# User router
app.include_router(
    fastapi_users.get_auth_router(auth_backends[0]),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"]
)

# S3 client setup
s3_client = boto3.client("s3")

# Sound upload endpoint
@app.post("/upload-sound/")
async def upload_sound(
    file: UploadFile = File(...),
    user: User = Depends(fastapi_users.current_user(active=True))
):
    # Check file size (1MB max)
    if file.size > 1 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 1MB")

    # Upload file to S3
    file_path = f"{user.id}/{file.filename}"
    s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, file_path)

    # Save file metadata to MongoDB
    sound_data = {
        "user_id": user.id,
        "sound_url": f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_path}",
        "sound_name": file.filename
    }
    result = await db["sounds"].insert_one(sound_data)

    return {"message": "File uploaded successfully", "sound_id": str(result.inserted_id)}

# Get user's sounds endpoint
@app.get("/sounds/")
async def get_sounds(user: User = Depends(fastapi_users.current_user(active=True))):
    sounds = await db["sounds"].find({"user_id": user.id}).to_list(None)
    return [
        {
            "id": str(sound["_id"]),
            "sound_name": sound["sound_name"],
            "sound_url": sound["sound_url"]
        }
        for sound in sounds
    ]
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)