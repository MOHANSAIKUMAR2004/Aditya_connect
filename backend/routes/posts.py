from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Post, Like, Comment, User, Notification
from ..security import current_user
from ..config import ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES, MAX_IMAGE_SIZE_MB, MAX_VIDEO_SIZE_MB

router = APIRouter(prefix="/api/posts", tags=["posts"])
BASE = Path(__file__).resolve().parents[1] / "uploads"

def serialize_post(p, db, uid):
    likes = db.query(Like).filter(Like.post_id == p.id).count()
    comments = db.query(Comment).filter(Comment.post_id == p.id).count()
    liked = db.query(Like).filter(Like.post_id == p.id, Like.user_id == uid).first() is not None
    return {"id": p.id, "caption": p.caption, "media_url": p.media_url, "media_type": p.media_type, "created_at": p.created_at.isoformat(), "author": {"id": p.author.id, "name": p.author.full_name, "username": p.author.username, "department": p.author.department}, "likes": likes, "comments": comments, "liked": liked}

@router.get("")
def list_posts(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(30).all()
    return [serialize_post(p, db, user.id) for p in posts]

@router.post("")
async def create_post(request: Request, caption: str = Form(""), media: UploadFile | None = File(None), db: Session = Depends(get_db)):
    user = current_user(request, db)
    media_url = None; media_type = "text"
    if media:
        if media.content_type in ALLOWED_IMAGE_TYPES:
            limit = MAX_IMAGE_SIZE_MB * 1024 * 1024
            folder, media_type = BASE / "images", "image"
        elif media.content_type in ALLOWED_VIDEO_TYPES:
            limit = MAX_VIDEO_SIZE_MB * 1024 * 1024
            folder, media_type = BASE / "videos", "video"
        else:
            raise HTTPException(400, "Unsupported media type")
        content = await media.read()
        if len(content) > limit:
            raise HTTPException(400, "File is too large")
        ext = Path(media.filename or "").suffix.lower() or ".bin"
        name = f"{uuid.uuid4().hex}{ext}"
        (folder / name).write_bytes(content)
        media_url = f"/uploads/{folder.name}/{name}"
    if not caption.strip() and not media_url:
        raise HTTPException(400, "Add text or media")
    p = Post(author_id=user.id, caption=caption.strip(), media_url=media_url, media_type=media_type)
    db.add(p); db.commit(); db.refresh(p)
    return serialize_post(p, db, user.id)

@router.post("/{post_id}/like")
def like(post_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    post = db.get(Post, post_id)
    if not post: raise HTTPException(404, "Post not found")
    existing = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
    if existing: db.delete(existing); action = "unliked"
    else:
        db.add(Like(user_id=user.id, post_id=post_id)); action = "liked"
        if post.author_id != user.id: db.add(Notification(user_id=post.author_id, message=f"{user.full_name} liked your post"))
    db.commit()
    return {"action": action, "likes": db.query(Like).filter(Like.post_id == post_id).count()}

@router.get("/{post_id}/comments")
def comments(post_id: int, db: Session = Depends(get_db)):
    rows = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()
    return [{"id": c.id, "body": c.body, "user": c.user.username, "name": c.user.full_name, "created_at": c.created_at.isoformat()} for c in rows]

@router.post("/{post_id}/comments")
def add_comment(post_id: int, request: Request, body: str = Form(...), db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not body.strip(): raise HTTPException(400, "Comment cannot be empty")
    post = db.get(Post, post_id)
    if not post: raise HTTPException(404, "Post not found")
    c = Comment(user_id=user.id, post_id=post_id, body=body.strip())
    db.add(c)
    if post.author_id != user.id: db.add(Notification(user_id=post.author_id, message=f"{user.full_name} commented on your post"))
    db.commit(); db.refresh(c)
    return {"id": c.id, "body": c.body, "user": user.username, "name": user.full_name}
