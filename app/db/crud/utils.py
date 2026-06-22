from sqlalchemy.orm import Session, joinedload
from typing import List

from ..models import Supplier, SupplierCategory


def get_suppliers_for_comparison(
    db: Session, 
    supplier_ids: List[int]
) -> List[Supplier]:
    """
    Получить нескольких поставщиков для сравнения со всеми данными.
    """
    return db.query(Supplier).options(
        joinedload(Supplier.categories).joinedload(SupplierCategory.category),
        joinedload(Supplier.contacts),
        joinedload(Supplier.order_conditions),
        joinedload(Supplier.certificates),
        joinedload(Supplier.notes)
    ).filter(
        Supplier.id.in_(supplier_ids),
        Supplier.status == 'active'
    ).all()
