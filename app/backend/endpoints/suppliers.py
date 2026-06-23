from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.crud import suppliers as crud
from app.schemas.supplier import SupplierResponse, SupplierCreate, SupplierUpdate, SupplierListResponse

from app.db.db_config import get_db

from .serializer import serialize_supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/", response_model=SupplierListResponse)
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    only_active: bool = True,
    db: Session = Depends(get_db)
):
    """Получить список всех поставщиков с пагинацией."""
    total = crud.get_suppliers_count(db, only_active=only_active)
    items = crud.get_all_suppliers(db, skip=skip, limit=limit, only_active=only_active)

    response_items = []
    for supplier in items:
        # Создаем словарь с данными поставщика
        response_items.append(serialize_supplier(supplier))
    
    return SupplierListResponse(
        total=total, 
        items=response_items, 
        skip=skip, 
        limit=limit
    )


@router.get("/search", response_model=SupplierListResponse)
def search_suppliers(
    query_text: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    has_certificates: Optional[bool] = Query(None),
    min_order_max: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Расширенный поиск поставщиков."""
    items = crud.search_suppliers(
        db=db,
        query_text=query_text,
        category_id=category_id,
        city=city,
        region=region,
        min_rating=min_rating,
        has_certificates=has_certificates,
        min_order_max=min_order_max,
        skip=skip,
        limit=limit
    )

    response_items = []
    for supplier in items:
        response_items.append(serialize_supplier(supplier))

    return SupplierListResponse(total=len(items), items=response_items, skip=skip, limit=limit)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Получить поставщика по ID."""
    supplier = crud.get_supplier(db, supplier_id)
    supplier = serialize_supplier(supplier)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(supplier_data: SupplierCreate, db: Session = Depends(get_db)):
    """Создать нового поставщика."""
    new_supplier = crud.create_supplier(db, supplier_data.model_dump())
    new_supplier = serialize_supplier(new_supplier)
    return new_supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier_data: SupplierUpdate, db: Session = Depends(get_db)):
    """Обновить данные поставщика."""
    supplier = crud.update_supplier(db, supplier_id, supplier_data.model_dump(exclude_unset=True))
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Удалить поставщика."""
    deleted = crud.delete_supplier(db, supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return None


@router.post("/{supplier_id}/rating/update", response_model=SupplierResponse)
def update_rating(supplier_id: int, db: Session = Depends(get_db)):
    """Пересчитать рейтинг поставщика на основе заметок."""
    supplier = crud.get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    crud.update_supplier_rating(db, supplier_id)
    db.refresh(supplier)
    return supplier
