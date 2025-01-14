from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import oauth2_scheme
import crud, schemas
from database import get_db

router = APIRouter()

@router.get("/user/orders", response_model=list[schemas.Order])
def get_user_orders(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_current_user(token, db)
    return crud.get_user_orders(db, user.id)
