from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from fastapi_users import FastAPIUsers, BaseUserManager
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from beanie import Document, Indexed, init_beanie
import boto3
from bson import ObjectId
from typing import Optional

# Configuration
DATABASE_URL = "mongodb://localhost:27017"
SECRET = "YOUR_SECRET_KEY"  # Replace with a secure secret key
S3_BUCKET_NAME = "your-s3-bucket-name"  # Replace with your S3 bucket name

# MongoDB setup
client = AsyncIOMotorClient(DATABASE_URL)
db = client["soundboard"]

# User model
class User(Document, BaseUserManager):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Settings:
        name = "users"

# Sound model
class Sound(Document):
    user_id: ObjectId
    sound_url: str
    sound_name: str

    class Settings:
        name = "sounds"

# User manager
class UserManager(ObjectIDIDMixin, BaseUserManager[User, ObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

# FastAPI app setup with lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    await init_beanie(database=db, document_models=[User])
    yield  # Hand control over to the application
    # Optionally, add shutdown logic here if necessary

# FastAPI app setup
app = FastAPI(lifespan=lifespan)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize the database
async def init_db():
    await init_beanie(database=db, document_models=[User])

# JWT Authentication setup
auth_backends = [
    JWTStrategy(secret=SECRET, lifetime_seconds=3600),
]

# Use the following link to fix this
# https://fastapi-users.github.io/fastapi-users/10.1/configuration/full-example/
# FastAPI Users setup
user_db = BeanieUserDatabase(User)
fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
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