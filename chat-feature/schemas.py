from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    max_participants: int = Field(default=100, ge=2, le=500)

class ChatRoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by_id: int
    max_participants: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    uuid: str
    chat_room_id: int  # Aligned with your models.py change
    user_id: int
    content: str
    message_type: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
