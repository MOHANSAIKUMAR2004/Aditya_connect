from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Request
from .config import SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=12)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def current_user(request: Request, db):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Please log in")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired session")
    from .models import User
    user = db.get(User, user_id)
    if not user or user.disabled:
        raise HTTPException(401, "Account unavailable")
    return user
