from app.database import users, db, init_db
from app.utils import get_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def create_initial_admin():
    # Check if admin user exists
    admin = await users.find_one({"is_admin": True})
    if admin:
        return
    
    # Create admin user
    admin_user = {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin"),  # Change this password after first login!
        "is_admin": True,
        "created_at": datetime.utcnow()
    }
    
    await users.insert_one(admin_user)
    print("Initial admin user created with username: admin and password: admin")
    print("Please change the password after first login!")

async def setup_database():
    # Create indexes
    await users.create_index("username", unique=True)
    await users.create_index("email", unique=True)
    await db.invitation_codes.create_index("code", unique=True)
    
    # Create initial admin user
    await create_initial_admin()

async def startup_db():
    await init_db() 