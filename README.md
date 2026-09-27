# Aditya Connect

A functional full-stack student social media starter built with FastAPI, SQLite, SQLAlchemy, JWT-in-HTTP-only-cookie authentication, vanilla HTML/CSS/JS, image/video posts, reels, likes, comments, follows, notifications, search, communities, events, reports, and an admin dashboard.

## Run on Windows PowerShell

```powershell
cd aditya-connect
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m backend.seed
uvicorn backend.main:app --reload --port 8000
```

Then open:

http://127.0.0.1:8000/

Demo accounts created by the seed script:

- admin@demo.local / Admin@12345
- mohan@demo.local / Student@12345
- priya@demo.local / Student@12345
- arjun@demo.local / Student@12345

These are fictional development accounts. Change them before deployment.

## Notes

- Uploaded media is stored under `backend/uploads`.
- SQLite is used locally.
- `ALLOWED_EMAIL_DOMAIN` is empty by default so demo accounts work. Set it to the real college domain before deployment if required.
- For production, replace local uploads with object storage and SQLite with PostgreSQL.
