from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date

from ..models import Certificate


def get_certificates_by_supplier(db: Session, supplier_id: int) -> List[Certificate]:
    """Получить все сертификаты поставщика."""
    return db.query(Certificate).filter(
        Certificate.supplier_id == supplier_id
    ).order_by(Certificate.expiry_date).all()


def get_valid_certificates(db: Session, supplier_id: int) -> List[Certificate]:
    """Получить только действующие сертификаты."""
    return db.query(Certificate).filter(
        Certificate.supplier_id == supplier_id,
        Certificate.is_valid == True
    ).all()


def create_certificate(db: Session, supplier_id: int, cert_data: Dict[str, Any]) -> Certificate:
    """Создать сертификат."""
    certificate = Certificate(supplier_id=supplier_id, **cert_data)
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    return certificate


def update_certificate(db: Session, certificate_id: int, cert_data: Dict[str, Any]) -> Optional[Certificate]:
    """Обновить сертификат."""
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        return None
    for key, value in cert_data.items():
        setattr(certificate, key, value)
    db.commit()
    db.refresh(certificate)
    return certificate


def update_certificate_validity(db: Session) -> int:
    """
    Обновить статус валидности всех сертификатов.
    Возвращает количество обновленных записей.
    """
    today = date.today()
    updated = db.query(Certificate).filter(
        Certificate.expiry_date < today,
        Certificate.is_valid == True
    ).update({"is_valid": False})
    db.commit()
    return updated


def delete_certificate(db: Session, certificate_id: int) -> bool:
    """Удалить сертификат."""
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        return False
    
    db.delete(certificate)
    db.commit()
    return True
