from fastapi import APIRouter, HTTPException, Depends
from app.models import Comment, CommentCreate
from app.database import comments
from typing import List
import markdown
from bson import ObjectId
from app.utils import get_current_user

router = APIRouter()

@router.post("/{post_id}", response_model=Comment)
async def create_comment(
    post_id: str,
    comment: CommentCreate,
    current_user: str = Depends(get_current_user)
):
    comment_dict = comment.dict()
    comment_dict["post_id"] = ObjectId(post_id)
    comment_dict["author_id"] = ObjectId(current_user)
    comment_dict["content"] = markdown.markdown(comment_dict["content"])
    
    result = await comments.insert_one(comment_dict)
    created_comment = await comments.find_one({"_id": result.inserted_id})
    return created_comment

@router.get("/post/{post_id}", response_model=List[Comment])
async def get_post_comments(post_id: str):
    cursor = comments.find({"post_id": ObjectId(post_id)}).sort("created_at", -1)
    return await cursor.to_list(length=None) 