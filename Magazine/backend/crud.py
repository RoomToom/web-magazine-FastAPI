from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from passlib.context import CryptContext
from jose import jwt
from backend.database import get_db
from backend.models import User, Product, CartItem, Order
from jose import jwt, JWTError
from backend.models import User, CartItem, Product, Order
from backend.database import SessionLocal
from backend.models import Product
from sqlalchemy.orm import Session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("1"))

SECRET_KEY = "secret"
ALGORITHM = "HS256"

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, is_admin: int = 0):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_admin(token: str):
    """
    Перевіряє, чи є користувач адміністратором.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token")
    except JWTError:
        raise ValueError("Invalid token")

    # Підключення до бази даних
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if not user or not user.is_admin:
        raise ValueError("User is not an admin")


def create_product(db: Session, product: schemas.ProductCreate):
    try:
        db_product = models.Product(
            name=product.name,
            price=product.price,
            category=product.category,
            image_url=product.image_url,
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()  # Відкочуємо транзакцію
        raise e

def get_products(db: Session, skip: int = 0, limit: int = 10):
    """
    Повертає список продуктів із бази даних із врахуванням пагінації.
    """
    return db.query(Product).offset(skip).limit(limit).all()

def delete_product(db: Session, product_id: int):
    """
    Видаляє продукт із бази даних за його ID.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise ValueError("Product not found")
    db.delete(product)
    db.commit()
    return product

def get_current_user(token: str, db: Session):
    """
    Отримує поточного користувача за токеном.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token")
    except JWTError:
        raise ValueError("Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("User not found")
    return user

def add_to_cart(db: Session, cart_item: schemas.CartItemCreate, user_id: int):
    """
    Додає товар до кошика або оновлює кількість, якщо товар уже є.
    """
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == user_id, CartItem.product_id == cart_item.product_id
    ).first()

    if existing_item:
        # Оновлюємо кількість
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Додаємо новий товар
        db_cart_item = CartItem(
            user_id=user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item


def get_cart_items_with_details(db: Session, user_id: int):
    """
    Отримує товари у кошику з деталями продуктів.
    """
    return db.query(CartItem, Product).join(Product, CartItem.product_id == Product.id).filter(CartItem.user_id == user_id).all()

def clear_cart(db: Session, user_id: int):
    """
    Очищає корзину користувача.
    """
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()

def create_order(db: Session, user_id: int):
    """
    Створює нове замовлення для користувача на основі товарів у його кошику.
    """
    # Отримуємо товари з кошика
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise ValueError("Cart is empty")

    # Створюємо замовлення
    order = Order(user_id=user_id, status="New")
    db.add(order)
    db.commit()
    db.refresh(order)

    # Переносимо товари з кошика до замовлення
    for item in cart_items:
        db.delete(item)  # Видаляємо з кошика
    db.commit()

    return order

def remove_cart_item(db: Session, cart_item_id: int):
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed successfully"}

