from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from ..models import Category, SupplierCategory


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Получить категорию по ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """Получить категорию по названию."""
    return db.query(Category).filter(Category.name.ilike(name)).first()


def get_all_categories(db: Session) -> List[Category]:
    """Получить все категории."""
    return db.query(Category).order_by(Category.name).all()


def get_root_categories(db: Session) -> List[Category]:
    """Получить корневые категории (без родителя)."""
    return db.query(Category).filter(Category.parent_id.is_(None)).order_by(Category.name).all()


def get_subcategories(db: Session, parent_id: int) -> List[Category]:
    """Получить дочерние категории."""
    return db.query(Category).filter(Category.parent_id == parent_id).order_by(Category.name).all()


def get_category_with_supplier_count(db: Session) -> List[Dict[str, Any]]:
    """Получить все категории с количеством поставщиков в каждой."""
    results = db.query(
        Category.id,
        Category.name,
        Category.created_at,
        func.count(SupplierCategory.supplier_id).label('supplier_count')
    ).outerjoin(
        SupplierCategory
    ).group_by(
        Category.id
    ).order_by(
        Category.name
    ).all()
    
    return [
        {"id": r.id, "name": r.name, "supplier_count": r.supplier_count, "created_at": r.created_at}
        for r in results
    ]


def create_category(db: Session, category_data: Dict[str, Any]) -> Category:
    """Создать новую категорию."""
    category = Category(**category_data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
