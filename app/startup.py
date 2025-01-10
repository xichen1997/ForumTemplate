from app.database import init_db

async def startup_db():
    await init_db() 