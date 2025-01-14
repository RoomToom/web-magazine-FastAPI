from backend.database import SessionLocal
from backend import crud

db = SessionLocal()
user = crud.authenticate_user(db, email="test@gmail.com", password="1")
print(user)
db.close()
