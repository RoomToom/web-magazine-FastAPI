from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import oauth2_scheme
import crud, schemas
from database import get_db

router = APIRouter()

@router.get("/cart", response_model=list[schemas.CartItem])
def get_cart_items(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    return crud.get_cart_items(db, user.id)

@router.post("/cart", response_model=schemas.CartItem)
def add_to_cart(item: schemas.CartItemCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    return crud.add_to_cart(db, item, user.id)

@router.delete("/cart/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    return crud.remove_from_cart(db, item_id, user.id)
