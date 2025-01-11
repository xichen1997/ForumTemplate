from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import asyncio
from pymongo.server_api import ServerApi

load_dotenv()

# Get MongoDB Atlas URL from environment variable
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

# Create a new client and connect to the server with MongoDB Atlas recommended settings
client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))

# Get database name from environment variable or use default
DB_NAME = os.getenv("DB_NAME", "forum_db")
db = client[DB_NAME]

# Collections
users = db.users
posts = db.posts
comments = db.comments

# Test the connection
async def test_connection():
    try:
        await client.admin.command('ping')
        print(f"Successfully connected to MongoDB Atlas! Using database: {DB_NAME}")
    except Exception as e:
        print(f"Unable to connect to MongoDB Atlas: {e}")
        raise e

# Ensure indexes
async def create_indexes():
    try:
        await users.create_index("username", unique=True)
        await users.create_index("email", unique=True)
        await posts.create_index("created_at")
        await comments.create_index([("post_id", 1), ("created_at", -1)])
        print("Database indexes created successfully!")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        raise e

# Initialize database
async def init_db():
    await test_connection()
    await create_indexes()

# Only create the task if we're running in an event loop
if asyncio.get_event_loop().is_running():
    asyncio.create_task(init_db())