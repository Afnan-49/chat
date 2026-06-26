from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import model.models as models
import schemas
from database import SessionLocal, engine
from auth import get_current_user, create_access_token, get_password_hash, verify_password
from datetime import timedelta

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Chat API",
    description="A real-time chat application built with FastAPI",
    version="1.0.0"
)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Authentication endpoints
@app.post("/auth/register", response_model=schemas.UserResponse)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(
        (models.User.email == user_data.email) |
        (models.User.username == user_data.username)
    ).first()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
@app.post("/auth/login")
async def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }
# Chat room endpoints
@app.post("/chatrooms/", response_model=schemas.ChatRoomResponse)
async def create_chat_room(
    chat_room_data: schemas.ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_chat_room = models.ChatRoom(
        name=chat_room_data.name,
        description=chat_room_data.description,
        created_by_id=current_user.id,
        max_participants=room_data.max_participants
    )

    db.add(db_chat_room)
    db.commit()
    db.refresh(db_chat_room)

    return db_chat_room
@app.get("/chat_rooms/", response_model=List[schemas.ChatRoomResponse])
async def get_chat_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    chat_rooms = db.query(models.ChatRoom).filter(models.ChatRoom.is_active == True)\
        .offset(skip).limit(limit).all()
    return chat_rooms
# Message endpoints
@app.get("/chat_rooms/{chat_room_id}/messages", response_model=List[schemas.MessageResponse])
async def get_chat_room_messages(
    chat_room_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    messages = db.query(models.Message).filter(models.Message.chat_room_id == chat_room_id)\
        .order_by(models.Message.created_at.desc())\
        .offset(skip).limit(limit).all()

    return messages[::-1]  # Return in chronological order
