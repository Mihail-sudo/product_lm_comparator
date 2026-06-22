from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..models import Contact


def get_contacts_by_supplier(db: Session, supplier_id: int) -> List[Contact]:
    """Получить все контакты поставщика."""
    return db.query(Contact).filter(Contact.supplier_id == supplier_id).all()


def get_primary_contact(db: Session, supplier_id: int) -> Optional[Contact]:
    """Получить основной контакт поставщика."""
    return db.query(Contact).filter(
        Contact.supplier_id == supplier_id,
        Contact.is_primary == True
    ).first()


def create_contact(db: Session, supplier_id: int, contact_data: Dict[str, Any]) -> Contact:
    """Создать контакт для поставщика."""
    contact = Contact(supplier_id=supplier_id, **contact_data)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(db: Session, contact_id: int, contact_data: Dict[str, Any]) -> Optional[Contact]:
    """Обновить контакт."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        return None
    
    for key, value in contact_data.items():
        setattr(contact, key, value)
    
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int) -> bool:
    """Удалить контакт."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        return False
    
    db.delete(contact)
    db.commit()
    return True
