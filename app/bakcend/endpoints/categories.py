from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.crud import categories as crud
from schemas.category import CategoryResponse, CategoryCreate, CategoryWithSupplierCount
from db.db_config import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """Получить все категории."""
    return crud.get_all_categories(db)


@router.get("/root", response_model=List[CategoryResponse])
def get_root_categories(db: Session = Depends(get_db)):
    """Получить корневые категории."""
    return crud.get_root_categories(db)


@router.get("/{category_id}/subcategories", response_model=List[CategoryResponse])
def get_subcategories(category_id: int, db: Session = Depends(get_db)):
    """Получить дочерние категории."""
    return crud.get_subcategories(db, category_id)


@router.get("/with-count", response_model=List[CategoryWithSupplierCount])
def get_categories_with_supplier_count(db: Session = Depends(get_db)):
    """Получить все категории с количеством поставщиков."""
    return crud.get_category_with_supplier_count(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Получить категорию по ID."""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Создать новую категорию."""
    return crud.create_category(db, category_data.model_dump())
