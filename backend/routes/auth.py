from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..security import hash_password, verify_password, create_token, current_user
from ..config import ALLOWED_EMAIL_DOMAIN

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterIn(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    department: str = "MCA"
    year: str = "1st Year"
    section: str = "A"

class LoginIn(BaseModel):
    identifier: str
    password: str

@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if len(data.password) < 8:
        raise HTTPException(400, "Password must contain at least 8 characters")
    email = data.email.lower().strip()
    if ALLOWED_EMAIL_DOMAIN and not email.endswith("@" + ALLOWED_EMAIL_DOMAIN):
        raise HTTPException(400, "Use your college email address")
    if db.query(User).filter((User.email == email) | (User.username == data.username.lower())).first():
        raise HTTPException(400, "Email or username already exists")
    user = User(
        full_name=data.full_name.strip(),
        username=data.username.lower().strip(),
        email=email,
        password_hash=hash_password(data.password),
        department=data.department,
        year=data.year,
        section=data.section,
    )
    db.add(user); db.commit(); db.refresh(user)
    return {"message": "Account created", "username": user.username}

@router.post("/login")
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    identifier = data.identifier.lower().strip()
    user = db.query(User).filter((User.email == identifier) | (User.username == identifier)).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user.id)
    response.set_cookie("access_token", token, httponly=True, samesite="lax", secure=False, max_age=43200)
    return {"message": "Logged in", "user": {"id": user.id, "username": user.username, "full_name": user.full_name}}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    return {"id": user.id, "full_name": user.full_name, "username": user.username, "email": user.email, "department": user.department, "year": user.year, "section": user.section, "bio": user.bio, "avatar": user.avatar, "role": user.role, "is_private": user.is_private}
