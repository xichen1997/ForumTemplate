from fastapi import APIRouter, HTTPException, Depends, Form
from app.models import Comment, CommentCreate
from app.database import comments
from typing import List
import markdown
from bson import ObjectId
from app.utils import get_current_user
from datetime import datetime
from fastapi.responses import RedirectResponse, Response

router = APIRouter()

@router.post("/{post_id}")
async def create_comment(
    post_id: str,
    content: str = Form(...),
    current_user: str = Depends(get_current_user)
):
    comment_dict = {
        "content": content,
        "post_id": ObjectId(post_id),
        "author_id": ObjectId(current_user),
        "created_at": datetime.utcnow()
    }
    
    result = await comments.insert_one(comment_dict)
    return RedirectResponse(url="/", status_code=303)

@router.get("/post/{post_id}", response_model=List[Comment])
async def get_post_comments(post_id: str):
    cursor = comments.find({"post_id": ObjectId(post_id)}).sort("created_at", -1)
    return await cursor.to_list(length=None) 

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: str = Depends(get_current_user)
):
    # Check if comment exists
    comment = await comments.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is the author
    if str(comment["author_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    # Delete the comment
    await comments.delete_one({"_id": ObjectId(comment_id)})
    return Response(status_code=204)

@router.post("/{comment_id}/delete")
async def delete_comment_with_post(
    comment_id: str,
    current_user: str = Depends(get_current_user)
):
    # Check if comment exists
    comment = await comments.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is the author
    if str(comment["author_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    # Delete the comment
    await comments.delete_one({"_id": ObjectId(comment_id)})
    return RedirectResponse(url="/", status_code=303) 