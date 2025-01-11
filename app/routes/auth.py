from fastapi import APIRouter, HTTPException, status, Form, Request, Response
from fastapi.responses import RedirectResponse
from app.database import users
from app.utils import verify_password, get_password_hash, create_access_token
from typing import Optional
from datetime import timedelta

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
    
    result = await users.insert_one(user_dict)
    return RedirectResponse(url="/login", status_code=302)

@router.post("/token")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
):
    user = await users.find_one({"username": username})
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=timedelta(minutes=60)
    )
    
    # Set the token as an HTTP-only cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600,
        secure=True,
        samesite="lax"
    )
    
    return response

@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response 