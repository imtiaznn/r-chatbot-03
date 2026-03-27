import uuid

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class Sender(Enum.enum):
    user        = "user"
    bot         = "bot"

class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    sid         = Column(String)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp   = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    duration_ms = Column(Float)
    data        = Column(String)

class Sessions(Base):
    __tablename__ = "sessions"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    timestamp   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    messages    = relationship("Messages", back_populates="session") # one-to-many
    user        = relationship("Users", back_populates="sessions")

class Users(Base):
    __tablename__ = "users"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name        = Column(String(100), nullable=False)
    email       = Column(String(200), nullable=False, unique=True)

    sessions    = relationship("Sessions", back_populates="user")

class Messages(Base):
    __tablename__ = "messages"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id  = Column(Integer, ForeignKey("sessions.id"))
    text        = Column(String)
    sender      = Column(Enum(Sender), nullable=False)
    timestamp   = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session     = relationship("Sessions", back_populates="messages")
