from sqlalchemy import create_engine
from database import Base  # Adjust this import path if 'database.py' is in a different folder
from model.models import ChatRoom, Message, User
from sqlalchemy.orm import DeclarativeBase

# Create async engine the connection pool to PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

class Base(DeclarativeBase):
    pass