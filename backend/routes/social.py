from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Notification, Community, Event
from ..security import current_user

router = APIRouter(prefix="/api", tags=["social"])

@router.get("/notifications")
def notifications(request: Request, db: Session = Depends(get_db)):
    u = current_user(request, db)
    rows = db.query(Notification).filter(Notification.user_id == u.id).order_by(Notification.created_at.desc()).limit(50).all()
    return [{"id":n.id,"message":n.message,"read":n.read,"created_at":n.created_at.isoformat()} for n in rows]

@router.post("/notifications/read")
def read_notifications(request: Request, db: Session = Depends(get_db)):
    u = current_user(request, db)
    db.query(Notification).filter(Notification.user_id == u.id).update({"read": True})
    db.commit()
    return {"message":"ok"}

@router.get("/communities")
def communities(request: Request, db: Session = Depends(get_db)):
    current_user(request, db)
    return [{"id":c.id,"name":c.name,"description":c.description} for c in db.query(Community).all()]

@router.get("/events")
def events(request: Request, db: Session = Depends(get_db)):
    current_user(request, db)
    return [{"id":e.id,"title":e.title,"description":e.description,"date":e.date,"location":e.location} for e in db.query(Event).all()]
