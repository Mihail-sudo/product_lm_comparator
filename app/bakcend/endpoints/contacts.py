from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.crud import contacts as crud
from schemas.contact import ContactResponse, ContactCreate
from db.db_config import get_db

router = APIRouter(prefix="/suppliers/{supplier_id}/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
def get_contacts_by_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Получить все контакты поставщика."""
    return crud.get_contacts_by_supplier(db, supplier_id)


@router.get("/primary", response_model=ContactResponse)
def get_primary_contact(supplier_id: int, db: Session = Depends(get_db)):
    """Получить основной контакт поставщика."""
    contact = crud.get_primary_contact(db, supplier_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Primary contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(supplier_id: int, contact_data: ContactCreate, db: Session = Depends(get_db)):
    """Создать контакт для поставщика."""
    return crud.create_contact(db, supplier_id, contact_data.model_dump())


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_data: ContactCreate, db: Session = Depends(get_db)):
    """Обновить контакт."""
    contact = crud.update_contact(db, contact_id, contact_data.model_dump())
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Удалить контакт."""
    deleted = crud.delete_contact(db, contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None
