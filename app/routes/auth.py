from fastapi import APIRouter, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse
from app.database import users
from app.utils import verify_password, get_password_hash
from typing import Optional

router = APIRouter()

@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    # Check if username exists
    if await users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_dict = {
        "username": username,
        "email": email,
        "hashed_password": get_password_hash(password)
    }
    
    await users.insert_one(user_dict)
    return RedirectResponse(url="/login", status_code=302)

@router.post("/token")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    user = await users.find_one({"username": username})
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return RedirectResponse(url="/", status_code=302)

@router.get("/logout")
async def logout():
    return RedirectResponse(url="/login", status_code=302) 