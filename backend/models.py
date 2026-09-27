from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    department: Mapped[str] = mapped_column(String(80), default="MCA")
    year: Mapped[str] = mapped_column(String(30), default="1st Year")
    section: Mapped[str] = mapped_column(String(30), default="A")
    bio: Mapped[str] = mapped_column(String(300), default="")
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="student")
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    caption: Mapped[str] = mapped_column(Text, default="")
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), default="text")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    author = relationship("User")

class Like(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"), nullable=True, index=True)
    reel_id: Mapped[int | None] = mapped_column(ForeignKey("reels.id"), nullable=True, index=True)
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_post_like"), UniqueConstraint("user_id", "reel_id", name="uq_reel_like"))

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"), nullable=True)
    reel_id: Mapped[int | None] = mapped_column(ForeignKey("reels.id"), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    user = relationship("User")

class Follow(Base):
    __tablename__ = "follows"
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow"),)

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(String(300))
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Reel(Base):
    __tablename__ = "reels"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    caption: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[str] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    author = relationship("User")

class Community(Base):
    __tablename__ = "communities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[str] = mapped_column(String(40))
    location: Mapped[str] = mapped_column(String(150))

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    target_type: Mapped[str] = mapped_column(String(30))
    target_id: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
