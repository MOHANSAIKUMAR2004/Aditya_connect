from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Post, Reel, Report
from ..security import current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

def admin(request, db):
    u = current_user(request, db)
    if u.role != "admin": raise HTTPException(403, "Admin access required")
    return u

@router.get("/stats")
def stats(request: Request, db: Session = Depends(get_db)):
    admin(request, db)
    return {"users":db.query(User).count(),"posts":db.query(Post).count(),"reels":db.query(Reel).count(),"reports":db.query(Report).count()}

@router.get("/users")
def users(request: Request, db: Session = Depends(get_db)):
    admin(request, db)
    return [{"id":u.id,"name":u.full_name,"username":u.username,"email":u.email,"role":u.role,"disabled":u.disabled} for u in db.query(User).order_by(User.id.desc()).all()]

@router.patch("/users/{user_id}/disable")
def disable(user_id:int, request:Request, db:Session=Depends(get_db)):
    admin(request, db)
    u=db.get(User,user_id)
    if not u: raise HTTPException(404,"User not found")
    u.disabled=not u.disabled; db.commit()
    return {"disabled":u.disabled}
