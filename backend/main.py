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