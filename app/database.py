from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import asyncio
from pymongo.server_api import ServerApi

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# Create a new client and connect to the server
client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
db = client.forum_db

# Collections
users = db.users
posts = db.posts
comments = db.comments

# Test the connection
async def test_connection():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Unable to connect to MongoDB: {e}")
        raise e

# Ensure indexes
async def create_indexes():
    await users.create_index("username", unique=True)
    await users.create_index("email", unique=True)
    await posts.create_index("created_at")
    await comments.create_index([("post_id", 1), ("created_at", -1)])

# Initialize database
async def init_db():
    await test_connection()
    await create_indexes()

# Run initialization
asyncio.create_task(init_db()) 