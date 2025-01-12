from fastapi import APIRouter, HTTPException, status, Form, Request, Response, Depends
from fastapi.responses import RedirectResponse
from app.database import users, db
from app.utils import verify_password, get_password_hash, create_access_token, get_current_user, require_current_user
from typing import Optional
from datetime import timedelta, datetime
import secrets
from bson import ObjectId

router = APIRouter()

async def require_admin(request: Request):
    user_id = await require_current_user(request)
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id

@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    invitation_code: str = Form(...)
):
    # Verify invitation code
    invite = await db.invitation_codes.find_one({
        "code": invitation_code,
        "used_by": None
    })
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or used invitation code")

    # Check if username exists
    if await users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_dict = {
        "username": username,
        "email": email,
        "hashed_password": get_password_hash(password),
        "is_admin": False
    }
    
    result = await users.insert_one(user_dict)
    
    # Mark invitation code as used
    await db.invitation_codes.update_one(
        {"_id": invite["_id"]},
        {
            "$set": {
                "used_by": result.inserted_id,
                "used_at": datetime.utcnow()
            }
        }
    )
    
    return RedirectResponse(url="/login", status_code=302)

@router.post("/generate-invite")
async def generate_invite(request: Request):
    user_id = await require_admin(request)
    
    code = secrets.token_urlsafe(16)
    await db.invitation_codes.insert_one({
        "code": code,
        "created_by": ObjectId(user_id),
        "created_at": datetime.utcnow(),
        "used_by": None,
        "used_at": None
    })
    
    return {"code": code}

@router.post("/login")
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
    
    # Create response with cookie
    response = RedirectResponse(url="/", status_code=303)  # Using 303 for POST-to-GET redirect
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