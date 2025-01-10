from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import User
from app.database import users
from app.utils import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from bson import ObjectId
from pydantic import BaseModel

# Add this new model for registration
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Update the register endpoint
@router.post("/register")
async def register(user: UserCreate):
    # Check if username exists
    if await users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": get_password_hash(user.password)
    }
    
    result = await users.insert_one(user_dict)
    return {"message": "User created successfully"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"} 