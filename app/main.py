from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from app.routes import auth, posts, comments
from app.startup import startup_db
from app.utils import get_current_user
from app.database import users, posts as posts_collection
from bson import ObjectId
from datetime import datetime

app = FastAPI(title="Forum API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates configuration
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.on_event("startup")
async def startup():
    await startup_db()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    current_user = None
    try:
        user_id = await get_current_user(request)
        if user_id:
            current_user = await users.find_one({"_id": ObjectId(user_id)})
            if current_user:
                current_user["is_authenticated"] = True
    except:
        pass

    # Get all posts with author information
    cursor = posts_collection.find().sort("created_at", -1)
    all_posts = await cursor.to_list(length=None)
    
    # Format posts for template
    formatted_posts = []
    for post in all_posts:
        author = await users.find_one({"_id": post["author_id"]})
        formatted_post = {
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "created_at": post.get("created_at", datetime.utcnow()),
            "author": {
                "username": author["username"] if author else "Unknown",
                "id": str(post["author_id"])
            }
        }
        formatted_posts.append(formatted_post)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": formatted_posts,
        "current_user": current_user or {"is_authenticated": False}
    })

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    current_user = None
    try:
        user_id = await get_current_user(request)
        if user_id:
            return RedirectResponse(url="/")
    except:
        pass
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": current_user or {"is_authenticated": False}
    })

@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    current_user = None
    try:
        user_id = await get_current_user(request)
        if user_id:
            return RedirectResponse(url="/")
    except:
        pass
    
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "current_user": current_user or {"is_authenticated": False}
    })

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    try:
        user_id = await get_current_user(request)
        if not user_id:
            return RedirectResponse(url="/login")
        current_user = await users.find_one({"_id": ObjectId(user_id)})
        if not current_user:
            return RedirectResponse(url="/login")
    except:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": current_user
    }) 