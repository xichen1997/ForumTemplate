from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, posts, comments
from app.startup import startup_db

app = FastAPI(title="Forum API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await startup_db()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Forum API"} 