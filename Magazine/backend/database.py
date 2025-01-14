import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import os
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@db:5432/magazine")


# Створюємо engine
engine = None
while engine is None:
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        engine.connect()  # Пробуємо підключитися
    except OperationalError:
        print("Database is not ready, retrying in 5 seconds...")
        time.sleep(5)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Функція для отримання сесії бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
