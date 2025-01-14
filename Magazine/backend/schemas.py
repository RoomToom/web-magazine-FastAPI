from pydantic import BaseModel
from typing import Optional
from backend.database import get_db

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: int

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    image_url: Optional[str] = None

class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItem(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class Order(BaseModel):
    id: int
    status: str

class Config:
    from_attributes = True

class ProductInCart(BaseModel):
    id: int
    name: str
    price: float
    category: str
    image_url: Optional[str]

    class Config:
        orm_mode = True

class CartItemWithDetails(BaseModel):
    id: int
    product: ProductInCart
    quantity: int

class Config:
    orm_mode = True


class CartItemUpdate(BaseModel):
    quantity: int