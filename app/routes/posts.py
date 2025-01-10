from fastapi import APIRouter, HTTPException, Depends
from app.models import Post, PostCreate
from app.database import posts
from typing import List
import markdown
from bson import ObjectId
from app.utils import get_current_user

router = APIRouter()

@router.post("/", response_model=Post)
async def create_post(post: PostCreate, current_user: str = Depends(get_current_user)):
    post_dict = post.dict()
    post_dict["author_id"] = ObjectId(current_user)
    post_dict["content"] = markdown.markdown(post_dict["content"])
    
    result = await posts.insert_one(post_dict)
    created_post = await posts.find_one({"_id": result.inserted_id})
    return created_post

@router.get("/", response_model=List[Post])
async def get_posts():
    cursor = posts.find().sort("created_at", -1)
    return await cursor.to_list(length=None)

@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str):
    post = await posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post 