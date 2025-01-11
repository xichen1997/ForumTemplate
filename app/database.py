from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# Get MongoDB Atlas URL from environment variable
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)

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