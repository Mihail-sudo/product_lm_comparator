from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..models import OrderCondition


def get_order_conditions_by_supplier(db: Session, supplier_id: int) -> List[OrderCondition]:
    """Получить все условия заказа поставщика."""
    return db.query(OrderCondition).filter(
        OrderCondition.supplier_id == supplier_id
    ).all()


def get_order_conditions_by_supplier_and_category(
    db: Session, 
    supplier_id: int, 
    category_id: int
) -> Optional[OrderCondition]:
    """Получить условия заказа для конкретной категории."""
    return db.query(OrderCondition).filter(
        OrderCondition.supplier_id == supplier_id,
        OrderCondition.category_id == category_id
    ).first()


def create_order_condition(
    db: Session, 
    supplier_id: int, 
    condition_data: Dict[str, Any]
) -> OrderCondition:
    """Создать условие заказа."""
    condition = OrderCondition(supplier_id=supplier_id, **condition_data)
    db.add(condition)
    db.commit()
    db.refresh(condition)
    return condition


def update_order_condition(
    db: Session, 
    condition_id: int, 
    condition_data: Dict[str, Any]
) -> Optional[OrderCondition]:
    """Обновить условие заказа."""
    condition = db.query(OrderCondition).filter(OrderCondition.id == condition_id).first()
    if not condition:
        return None
    
    for key, value in condition_data.items():
        setattr(condition, key, value)
    
    db.commit()
    db.refresh(condition)
    return condition
