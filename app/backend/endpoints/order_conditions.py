from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.crud import order_conditions as crud
from app.schemas.order_condition import OrderConditionResponse, OrderConditionCreate
from app.db.db_config import get_db

router = APIRouter(prefix="/suppliers/{supplier_id}/order-conditions", tags=["order_conditions"])


@router.get("/", response_model=List[OrderConditionResponse])
def get_order_conditions(supplier_id: int, db: Session = Depends(get_db)):
    """Получить все условия заказа поставщика."""
    return crud.get_order_conditions_by_supplier(db, supplier_id)


@router.get("/category/{category_id}", response_model=OrderConditionResponse)
def get_order_condition_by_category(supplier_id: int, category_id: int, db: Session = Depends(get_db)):
    """Получить условия заказа для конкретной категории."""
    condition = crud.get_order_conditions_by_supplier_and_category(db, supplier_id, category_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Order condition not found")
    return condition


@router.post("/", response_model=OrderConditionResponse, status_code=201)
def create_order_condition(supplier_id: int, condition_data: OrderConditionCreate, db: Session = Depends(get_db)):
    """Создать условие заказа."""
    return crud.create_order_condition(db, supplier_id, condition_data.model_dump())


@router.put("/{condition_id}", response_model=OrderConditionResponse)
def update_order_condition(condition_id: int, condition_data: OrderConditionCreate, db: Session = Depends(get_db)):
    """Обновить условие заказа."""
    condition = crud.update_order_condition(db, condition_id, condition_data.model_dump())
    if not condition:
        raise HTTPException(status_code=404, detail="Order condition not found")
    return condition


@router.delete("/{condition_id}", status_code=204)
def delete_order_condition(condition_id: int, db: Session = Depends(get_db)):
    """Удалить условие заказа."""
    deleted = crud.delete_order_condition(db, condition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order condition not found")
    return None
