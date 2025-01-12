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
        print("Admin user already exists")
        return
    
    # Create admin user with environment variables or defaults
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    
    admin_user = {
        "username": admin_username,
        "email": admin_email,
        "hashed_password": get_password_hash(admin_password),
        "is_admin": True,
        "created_at": datetime.utcnow()
    }
    
    try:
        await users.insert_one(admin_user)
        print(f"""
Initial admin user created successfully!
Username: {admin_username}
Password: {admin_password}
Email: {admin_email}

IMPORTANT: Please change the password after first login!
        """)
    except Exception as e:
        print(f"Error creating admin user: {e}")

async def setup_database():
    # Initialize database first
    await init_db()
    
    # Create indexes
    try:
        await users.create_index("username", unique=True)
        await users.create_index("email", unique=True)
        await db.invitation_codes.create_index("code", unique=True)
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
    
    # Create initial admin user
    await create_initial_admin()

async def startup_db():
    print("Starting database setup...")
    
    # Initialize database collections
    if not await init_db():
        print("Failed to initialize database collections")
        return
    
    # Create indexes
    try:
        await users.create_index("username", unique=True)
        await users.create_index("email", unique=True)
        await db.invitation_codes.create_index("code", unique=True)
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        return
    
    # Create initial admin user
    await create_initial_admin()
    
    print("Database setup completed") 