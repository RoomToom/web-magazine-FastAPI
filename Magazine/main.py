from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from starlette import status

from backend import models, crud, database
from backend.database import engine
from sqlalchemy.testing import db
from fastapi.staticfiles import StaticFiles
from backend import models, schemas, crud
from backend.database import SessionLocal, engine, get_db
from backend.crud import verify_admin, get_current_user
import time
from backend.crud import get_products
from sqlalchemy import inspect
from backend.crud import delete_product
from backend.crud import create_order
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from backend.database import get_db
from backend import crud, models

from backend.models import User

db = SessionLocal()


start_time = time.time()
inspector = inspect(engine)
if not inspector.has_table("users"):
    models.Base.metadata.create_all(bind=engine)
print(f"Database setup completed in {time.time() - start_time} seconds")


db.close()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342", "http://127.0.0.1:8000"],  # Для локальної розробки залиште "*". Для production — вкажіть конкретні домени.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user, is_admin=1)

@app.post("/auth/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = crud.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/products", response_model=List[schemas.Product])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_product(db=db, product=product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    crud.verify_admin(token)
    return crud.delete_product(db=db, product_id=product_id)

@app.get("/cart", response_model=List[schemas.CartItemWithDetails])
def get_cart(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    cart_items = crud.get_cart_items_with_details(db=db, user_id=user.id)

    # Форматуємо дані відповідно до схеми
    formatted_cart = [
        {
            "id": item.CartItem.id,
            "product": {
                "id": item.Product.id,
                "name": item.Product.name,
                "price": item.Product.price,
                "category": item.Product.category,
                "image_url": item.Product.image_url,
            },
            "quantity": item.CartItem.quantity,
        }
        for item in cart_items
    ]

    return formatted_cart

@app.post("/cart", response_model=schemas.CartItem)
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    return crud.add_to_cart(db=db, cart_item=cart_item, user_id=user.id)

@app.post("/orders", response_model=schemas.Order)
def place_order(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    return crud.create_order(db=db, user_id=user.id)

@app.delete("/cart", status_code=204)
def clear_cart(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Очищає корзину поточного користувача.
    """
    user = crud.get_current_user(token, db)
    crud.clear_cart(db=db, user_id=user.id)
    return {"detail": "Cart cleared successfully"}

@app.delete("/cart/{cart_item_id}", response_model=dict)  # Задайте, що відповідь - це dict
def remove_cart_item(cart_item_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return crud.remove_cart_item(db=db, cart_item_id=cart_item_id)
@app.put("/cart/{cart_item_id}")
def update_cart_item(cart_item_id: int, quantity: schemas.CartItemUpdate, db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    if quantity.quantity < 1:
        # Видаляємо товар, якщо кількість < 1
        db.delete(cart_item)
        db.commit()
        return {"message": "Cart item removed"}

    # Оновлюємо кількість товару
    cart_item.quantity = quantity.quantity
    db.commit()
    db.refresh(cart_item)
    return {"message": "Cart item updated", "cart_item": cart_item}
