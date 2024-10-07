from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, HttpUrl
from fastapi_users import FastAPIUsers, BaseUserManager, schemas
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from beanie import Document, Indexed, PydanticObjectId, init_beanie
from typing import Optional
import os

# Configuration
DATABASE_URL = os.environ.get("DB_URL")
SECRET = os.environ.get("SECRET")  # Replace with a secure secret key
FRONTEND_URL = os.environ.get("FRONTEND_URL")

# MongoDB setup
client = AsyncIOMotorClient(DATABASE_URL)
db = client["soundboard"]

# User model
class User(Document):
    email: Indexed(EmailStr, unique=True) # type: ignore
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Settings:
        name = "users"
        email_collation = None  # Add this line
        
class UserRead(schemas.BaseUser[PydanticObjectId]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

# Sound model
class Sound(Document):
    user_id: PydanticObjectId
    sound_url: HttpUrl
    sound_name: str

    class Settings:
        name = "sounds"

class SoundCreate(BaseModel):
    sound_url: HttpUrl
    sound_name: str

# User manager
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

# FastAPI app setup with lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    await init_beanie(database=db, document_models=[User, Sound])
    yield  # Hand control over to the application
    # Optionally, add shutdown logic here if necessary

# FastAPI app setup
app = FastAPI(lifespan=lifespan)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication backend setup
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: JWTStrategy(secret=SECRET, lifetime_seconds=3600),
)

async def get_user_db():
    yield BeanieUserDatabase(User)

# FastAPI Users setup
async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# FastAPI Users setup
fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])

# User router
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)


# Sound upload endpoint
@app.post("/upload-sound/")
async def upload_sound(
    sound: SoundCreate,
    user: User = Depends(fastapi_users.current_user(active=True))
):
    sound = Sound (
        user_id     = user.id,
        sound_url   = sound.sound_url,
        sound_name  = sound.sound_name
    )
    await sound.insert()

    return {"message": "Sound uploaded successfully", "sound_id": str(sound.id)}

# Get user's sounds endpoint
@app.get("/sounds/")
async def get_sounds(user: User = Depends(fastapi_users.current_user(active=True))):
    sounds = await Sound.find(Sound.user_id == user.id).to_list()
    return [
        {
            "id": str(sound.id),
            "sound_name": sound.sound_name,
            "sound_url": str(sound.sound_url)
        }
        for sound in sounds
    ]
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)