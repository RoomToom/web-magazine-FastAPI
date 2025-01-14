from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import verify_admin
import models, schemas, crud
from database import get_db

router = APIRouter()

@router.get("/admin/orders", response_model=list[schemas.Order])
def get_all_orders(db: Session = Depends(get_db), token: str = Depends(verify_admin)):
    return crud.get_all_orders(db)

@router.put("/admin/orders/{order_id}")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db), token: str = Depends(verify_admin)):
    return crud.update_order_status(db, order_id, status)
