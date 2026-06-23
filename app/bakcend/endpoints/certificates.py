from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.crud import certificates as crud
from schemas.certificate import CertificateResponse, CertificateCreate
from db.db_config import get_db

router = APIRouter(prefix="/suppliers/{supplier_id}/certificates", tags=["certificates"])


@router.get("/", response_model=List[CertificateResponse])
def get_certificates(supplier_id: int, only_valid: bool = False, db: Session = Depends(get_db)):
    """Получить все сертификаты поставщика."""
    if only_valid:
        return crud.get_valid_certificates(db, supplier_id)
    return crud.get_certificates_by_supplier(db, supplier_id)


@router.post("/", response_model=CertificateResponse, status_code=201)
def create_certificate(supplier_id: int, cert_data: CertificateCreate, db: Session = Depends(get_db)):
    """Создать сертификат."""
    return crud.create_certificate(db, supplier_id, cert_data.model_dump())


@router.put("/{certificate_id}", response_model=CertificateResponse)
def update_certificate(certificate_id: int, cert_data: CertificateCreate, db: Session = Depends(get_db)):
    """Обновить сертификат."""
    certificate = crud.update_certificate(db, certificate_id, cert_data.model_dump())
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate


@router.delete("/{certificate_id}", status_code=204)
def delete_certificate(certificate_id: int, db: Session = Depends(get_db)):
    """Удалить сертификат."""
    deleted = crud.delete_certificate(db, certificate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return None


@router.post("/update-validity", response_model=dict)
def update_certificates_validity(db: Session = Depends(get_db)):
    """Обновить статус валидности всех сертификатов."""
    updated = crud.update_certificate_validity(db)
    return {"updated_count": updated}
