from .database import Base, engine, SessionLocal
from .models import User, Post, Reel, Community, Event, Notification
from .security import hash_password
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)
db=SessionLocal()

def user(username,email,name,role="student"):
    u=db.query(User).filter(User.username==username).first()
    if not u:
        u=User(full_name=name,username=username,email=email,password_hash=hash_password("Admin@12345" if role=="admin" else "Student@12345"),department="MCA",year="1st Year",section="A",role=role,bio="Aditya student • Building • Learning")
        db.add(u); db.flush()
    return u

admin=user("admin","admin@demo.local","Aditya Admin","admin")
mohan=user("mohan","mohan@demo.local","Mohan Sai Kumar")
priya=user("priya","priya@demo.local","Priya Sharma")
arjun=user("arjun","arjun@demo.local","Arjun Kumar")

if db.query(Post).count()==0:
    db.add_all([
        Post(author_id=mohan.id,caption="Building something new for our campus community 🚀"),
        Post(author_id=priya.id,caption="MCA study session 📚 #MCA #CollegeLife"),
        Post(author_id=arjun.id,caption="Hackathon mode: ON 🔥"),
    ])
if db.query(Community).count()==0:
    db.add_all([
        Community(name="MCA Students",description="Connect with MCA students."),
        Community(name="Coding Club",description="Projects, coding challenges and tech events."),
        Community(name="Cybersecurity Club",description="Security, cryptography and ethical hacking."),
    ])
if db.query(Event).count()==0:
    db.add_all([
        Event(title="Aditya Tech Fest",description="Technology, projects and student innovation.",date="2026-10-10",location="Main Auditorium"),
        Event(title="AI Workshop",description="Hands-on introduction to modern AI.",date="2026-10-18",location="Seminar Hall"),
    ])
if db.query(Notification).count()==0:
    db.add(Notification(user_id=mohan.id,message="Welcome to Aditya Connect!"))
db.commit()
print("Seed complete.")
