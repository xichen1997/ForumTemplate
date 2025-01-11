from fastapi import APIRouter, HTTPException, Depends
from app.models import Post, PostCreate, PostUpdate
from app.database import posts
from typing import List
import markdown
from bson import ObjectId
from app.utils import get_current_user
from datetime import datetime

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

@router.patch("/{post_id}", response_model=Post)
async def update_post(post_id: str, post_update: PostUpdate, current_user: str = Depends(get_current_user)):
    # Check if post exists
    post = await posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is the author
    if str(post["author_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    # Prepare update data
    update_data = {}
    if post_update.title is not None:
        update_data["title"] = post_update.title
    if post_update.content is not None:
        update_data["content"] = markdown.markdown(post_update.content)
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
    
    updated_post = await posts.find_one({"_id": ObjectId(post_id)})
    return updated_post 