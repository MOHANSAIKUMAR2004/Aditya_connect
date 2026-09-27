from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Follow, Post, Reel, Notification
from ..security import current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/search")
def search(q: str = "", request: Request = None, db: Session = Depends(get_db)):
    current_user(request, db)
    q = q.strip()
    if not q: return []
    users = db.query(User).filter((User.username.ilike(f"%{q}%")) | (User.full_name.ilike(f"%{q}%"))).limit(20).all()
    return [{"id": u.id, "name": u.full_name, "username": u.username, "department": u.department, "avatar": u.avatar} for u in users]

@router.get("/{username}")
def profile(username: str, request: Request, db: Session = Depends(get_db)):
    me = current_user(request, db)
    u = db.query(User).filter(User.username == username.lower()).first()
    if not u: raise HTTPException(404, "User not found")
    followers = db.query(Follow).filter(Follow.following_id == u.id).count()
    following = db.query(Follow).filter(Follow.follower_id == u.id).count()
    posts = db.query(Post).filter(Post.author_id == u.id).count()
    reels = db.query(Reel).filter(Reel.author_id == u.id).count()
    followed = db.query(Follow).filter(Follow.follower_id == me.id, Follow.following_id == u.id).first() is not None
    return {"id":u.id,"name":u.full_name,"username":u.username,"email":u.email,"department":u.department,"year":u.year,"section":u.section,"bio":u.bio,"avatar":u.avatar,"followers":followers,"following":following,"posts":posts,"reels":reels,"followed":followed,"is_private":u.is_private}

@router.post("/{username}/follow")
def follow(username: str, request: Request, db: Session = Depends(get_db)):
    me = current_user(request, db)
    target = db.query(User).filter(User.username == username.lower()).first()
    if not target: raise HTTPException(404, "User not found")
    if target.id == me.id: raise HTTPException(400, "You cannot follow yourself")
    existing = db.query(Follow).filter(Follow.follower_id == me.id, Follow.following_id == target.id).first()
    if existing:
        db.delete(existing); action="unfollowed"
    else:
        db.add(Follow(follower_id=me.id, following_id=target.id))
        db.add(Notification(user_id=target.id, message=f"{me.full_name} started following you"))
        action="followed"
    db.commit()
    return {"action":action}

@router.patch("/me")
def update_me(request: Request, full_name: str = "", bio: str = "", department: str = "", year: str = "", section: str = "", db: Session = Depends(get_db)):
    u = current_user(request, db)
    if full_name.strip(): u.full_name = full_name.strip()
    if bio is not None: u.bio = bio.strip()
    if department.strip(): u.department = department.strip()
    if year.strip(): u.year = year.strip()
    if section.strip(): u.section = section.strip()
    db.commit()
    return {"message":"Profile updated"}
