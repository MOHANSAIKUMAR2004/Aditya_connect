from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import Base, engine
from .routes import auth, posts, reels, users, social, admin

BASE = Path(__file__).resolve().parents[1]
Path(BASE / "database").mkdir(exist_ok=True)
Path(BASE / "backend/uploads/images").mkdir(parents=True, exist_ok=True)
Path(BASE / "backend/uploads/videos").mkdir(parents=True, exist_ok=True)
Path(BASE / "backend/uploads/thumbnails").mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aditya Connect API", version="1.0.0")
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(reels.router)
app.include_router(users.router)
app.include_router(social.router)
app.include_router(admin.router)

app.mount("/uploads", StaticFiles(directory=str(BASE / "backend/uploads")), name="uploads")
app.mount("/static", StaticFiles(directory=str(BASE / "frontend")), name="static")

@app.get("/api/health")
def health():
    return {"status":"ok"}

@app.get("/{path:path}")
def frontend(path: str):
    if path.startswith("api/") or path.startswith("uploads/"):
        return {"detail":"Not found"}
    target = BASE / "frontend" / (path if path else "index.html")
    if target.exists() and target.is_file():
        return FileResponse(target)
    return FileResponse(BASE / "frontend/index.html")
