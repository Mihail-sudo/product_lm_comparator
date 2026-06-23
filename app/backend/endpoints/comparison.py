from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.crud import utils as crud
from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.db.db_config import get_db

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.post("/", response_model=ComparisonResponse)
def compare_suppliers(request: ComparisonRequest, db: Session = Depends(get_db)):
    """
    Получить нескольких поставщиков для сравнения.
    Минимум 2 поставщика, максимум 5.
    """
    if len(request.supplier_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 suppliers for comparison")
    
    if len(request.supplier_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 suppliers for comparison")
    
    suppliers = crud.get_suppliers_for_comparison(db, request.supplier_ids)
    
    if len(suppliers) != len(request.supplier_ids):
        found_ids = [s.id for s in suppliers]
        missing = [id for id in request.supplier_ids if id not in found_ids]
        raise HTTPException(status_code=404, detail=f"Suppliers not found: {missing}")
    
    return ComparisonResponse(suppliers=suppliers)
