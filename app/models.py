from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class User(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Post(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    content: str
    author_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class CommentCreate(BaseModel):
    content: str

class Comment(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    post_id: PyObjectId
    author_id: PyObjectId
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None 