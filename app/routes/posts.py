from fastapi import APIRouter, HTTPException, Depends, Form, Response
from app.models import Post, PostCreate, PostUpdate
from app.database import posts, comments
from typing import List
import markdown
from bson import ObjectId
from app.utils import get_current_user
from datetime import datetime
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()

@router.post("/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    current_user: str = Depends(get_current_user)
):
    post_dict = {
        "title": title,
        "content": markdown.markdown(content),
        "author_id": ObjectId(current_user),
        "created_at": datetime.utcnow()
    }
    
    result = await posts.insert_one(post_dict)
    return RedirectResponse(url="/", status_code=303)

@router.get("/")
async def get_posts():
    cursor = posts.find().sort("created_at", -1)
    all_posts = await cursor.to_list(length=None)
    
    # Convert ObjectId to string for JSON response and add comments
    for post in all_posts:
        post["_id"] = str(post["_id"])
        post["author_id"] = str(post["author_id"])
        
        # Get comments for this post
        comments_cursor = comments.find({"post_id": ObjectId(post["_id"])}).sort("created_at", -1)
        post_comments = await comments_cursor.to_list(length=None)
        
        # Convert ObjectId to string in comments
        for comment in post_comments:
            comment["_id"] = str(comment["_id"])
            comment["post_id"] = str(comment["post_id"])
            comment["author_id"] = str(comment["author_id"])
        
        post["comments"] = post_comments
    
    return JSONResponse(content=all_posts)

@router.get("/{post_id}")
async def get_post(post_id: str):
    post = await posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Convert ObjectId to string for JSON response
    post["_id"] = str(post["_id"])
    post["author_id"] = str(post["author_id"])
    
    # Get comments for this post
    cursor = comments.find({"post_id": ObjectId(post_id)}).sort("created_at", -1)
    post_comments = await cursor.to_list(length=None)
    
    # Convert ObjectId to string in comments
    for comment in post_comments:
        comment["_id"] = str(comment["_id"])
        comment["post_id"] = str(comment["post_id"])
        comment["author_id"] = str(comment["author_id"])
    
    post["comments"] = post_comments
    return JSONResponse(content=post)

@router.patch("/{post_id}")
async def update_post(
    post_id: str,
    title: str = Form(None),
    content: str = Form(None),
    current_user: str = Depends(get_current_user)
):
    # Check if post exists
    post = await posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is the author
    if str(post["author_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    # Prepare update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = markdown.markdown(content)
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
    
    updated_post = await posts.find_one({"_id": ObjectId(post_id)})
    # Convert ObjectId to string for JSON response
    updated_post["_id"] = str(updated_post["_id"])
    updated_post["author_id"] = str(updated_post["author_id"])
    return JSONResponse(content=updated_post)

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    current_user: str = Depends(get_current_user)
):
    # Check if post exists
    post = await posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is the author
    if str(post["author_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete the post
    await posts.delete_one({"_id": ObjectId(post_id)})
    return Response(status_code=204)

@router.post("/{post_id}/delete")
async def delete_post_with_post(
    post_id: str,
    current_user: str = Depends(get_current_user)
):
    # Check if post exists
    post = await posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is the author
    if str(post["author_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete the post
    await posts.delete_one({"_id": ObjectId(post_id)})
    return RedirectResponse(url="/", status_code=303) 