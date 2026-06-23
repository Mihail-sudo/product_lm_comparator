from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, desc, func
from typing import List, Optional, Dict, Any

from ..models import (
    Supplier, SupplierCategory,
    OrderCondition, Certificate,
)


def get_supplier(db: Session, supplier_id: int) -> Optional[Supplier]:
    """Получить поставщика по ID со всеми связями."""
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def get_all_suppliers(db: Session, skip: int = 0, limit: int = 100, only_active: bool = True) -> List[Supplier]:
    """Получить список всех поставщиков с пагинацией."""
    query = db.query(Supplier).options(
        selectinload(Supplier.categories).selectinload(SupplierCategory.category)
    )
    if only_active:
        query = query.filter(Supplier.status == 'active')
    return query.offset(skip).limit(limit).all()


def get_suppliers_count(db: Session, only_active: bool = True) -> int:
    """Получить общее количество поставщиков."""
    query = db.query(func.count(Supplier.id))
    if only_active:
        query = query.filter(Supplier.status == 'active')
    return query.scalar()


def create_supplier(db: Session, supplier_data: Dict[str, Any]) -> Supplier:
    """Создать нового поставщика."""
    category_ids = supplier_data.pop('category_ids', None)

    supplier = Supplier(**supplier_data)
    db.add(supplier)
    db.flush()

    if category_ids:
        for category_id in category_ids:
            supplier_category = SupplierCategory(
                supplier_id=supplier.id,
                category_id=category_id,
                is_main=False
            )
            db.add(supplier_category)

    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier_id: int, supplier_data: Dict[str, Any]) -> Optional[Supplier]:
    """Обновить данные поставщика."""
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        return None
    
    for key, value in supplier_data.items():
        setattr(supplier, key, value)
    
    db.commit()
    db.refresh(supplier)
    return supplier


def delete_supplier(db: Session, supplier_id: int) -> bool:
    """Удалить поставщика (каскадно удалит все связанные записи)."""
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        return False
    
    db.delete(supplier)
    db.commit()
    return True


def search_suppliers(
    db: Session,
    query_text: Optional[str] = None,
    category_id: Optional[int] = None,
    city: Optional[str] = None,
    region: Optional[str] = None,
    min_rating: Optional[float] = None,
    has_certificates: Optional[bool] = None,
    min_order_max: Optional[float] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Supplier]:
    """
    Расширенный поиск поставщиков по различным критериям.
    """
    # Базовый запрос с загрузкой связанных данных
    query = db.query(Supplier).options(
        joinedload(Supplier.categories).joinedload(SupplierCategory.category),
        joinedload(Supplier.contacts)
    )
    
    # Только активные
    query = query.filter(Supplier.status == 'active')
    
    # Поиск по тексту (название или описание)
    if query_text:
        search_pattern = f"%{query_text}%"
        query = query.filter(
            or_(
                Supplier.name.ilike(search_pattern),
                Supplier.description.ilike(search_pattern)
            )
        )
    
    # Фильтр по категории
    if category_id:
        query = query.join(Supplier.categories).filter(
            SupplierCategory.category_id == category_id
        )
    
    # Фильтр по городу
    if city:
        query = query.filter(Supplier.city.ilike(f"%{city}%"))
    
    # Фильтр по региону
    if region:
        query = query.filter(Supplier.region.ilike(f"%{region}%"))
    
    # Фильтр по минимальному рейтингу
    if min_rating is not None:
        query = query.filter(Supplier.rating >= min_rating)
    
    # Фильтр по наличию сертификатов
    if has_certificates is True:
        query = query.join(Supplier.certificates).filter(
            Certificate.is_valid == True
        ).distinct()
    
    # Фильтр по максимальному минимальному заказу
    if min_order_max is not None:
        query = query.join(Supplier.order_conditions).filter(
            OrderCondition.min_order_quantity <= min_order_max
        ).distinct()
    
    # Сортировка по рейтингу (по убыванию)
    query = query.order_by(desc(Supplier.rating))
    
    return query.offset(skip).limit(limit).all()
