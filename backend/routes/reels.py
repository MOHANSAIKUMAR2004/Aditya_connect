from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Reel, Like, Comment, User, Notification
from ..security import current_user
from ..config import ALLOWED_VIDEO_TYPES, MAX_VIDEO_SIZE_MB

router = APIRouter(prefix="/api/reels", tags=["reels"])
BASE = Path(__file__).resolve().parents[1] / "uploads/videos"

def ser(r, db, uid):
    return {"id": r.id, "caption": r.caption, "video_url": r.video_url, "views": r.views, "created_at": r.created_at.isoformat(), "author": {"id": r.author.id, "name": r.author.full_name, "username": r.author.username}, "likes": db.query(Like).filter(Like.reel_id == r.id).count(), "liked": db.query(Like).filter(Like.reel_id == r.id, Like.user_id == uid).first() is not None}

@router.get("")
def list_reels(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    return [ser(r, db, user.id) for r in db.query(Reel).order_by(Reel.created_at.desc()).limit(30).all()]

@router.post("")
async def create_reel(request: Request, caption: str = Form(""), video: UploadFile = File(...), db: Session = Depends(get_db)):
    user = current_user(request, db)
    if video.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(400, "Use MP4, WebM or MOV video")
    data = await video.read()
    if len(data) > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, "Video is too large")
    ext = Path(video.filename or "").suffix.lower() or ".mp4"
    name = f"{uuid.uuid4().hex}{ext}"
    (BASE / name).write_bytes(data)
    r = Reel(author_id=user.id, caption=caption.strip(), video_url=f"/uploads/videos/{name}")
    db.add(r); db.commit(); db.refresh(r)
    return ser(r, db, user.id)

@router.post("/{reel_id}/like")
def like_reel(reel_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    reel = db.get(Reel, reel_id)
    if not reel: raise HTTPException(404, "Reel not found")
    existing = db.query(Like).filter(Like.reel_id == reel_id, Like.user_id == user.id).first()
    if existing: db.delete(existing); action = "unliked"
    else:
        db.add(Like(user_id=user.id, reel_id=reel_id)); action = "liked"
        if reel.author_id != user.id: db.add(Notification(user_id=reel.author_id, message=f"{user.full_name} liked your reel"))
    db.commit()
    return {"action": action, "likes": db.query(Like).filter(Like.reel_id == reel_id).count()}

@router.post("/{reel_id}/view")
def view_reel(reel_id: int, request: Request, db: Session = Depends(get_db)):
    current_user(request, db)
    reel = db.get(Reel, reel_id)
    if not reel: raise HTTPException(404, "Reel not found")
    reel.views += 1
    db.commit()
    return {"views": reel.views}
