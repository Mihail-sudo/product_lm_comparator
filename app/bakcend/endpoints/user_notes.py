from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.crud import user_notes as crud
from schemas.user_note import UserNoteResponse, UserNoteCreate
from db.db_config import get_db

router = APIRouter(prefix="/suppliers/{supplier_id}/notes", tags=["notes"])


@router.get("/", response_model=List[UserNoteResponse])
def get_notes(supplier_id: int, db: Session = Depends(get_db)):
    """Получить все заметки о поставщике."""
    return crud.get_notes_by_supplier(db, supplier_id)


@router.post("/", response_model=UserNoteResponse, status_code=201)
def create_note(supplier_id: int, note_data: UserNoteCreate, db: Session = Depends(get_db)):
    """Создать заметку о поставщике."""
    return crud.create_note(db, supplier_id, note_data.model_dump())


@router.put("/{note_id}", response_model=UserNoteResponse)
def update_note(note_id: int, note_data: UserNoteCreate, db: Session = Depends(get_db)):
    """Обновить заметку."""
    note = crud.update_note(db, note_id, note_data.model_dump())
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Удалить заметку."""
    deleted = crud.delete_note(db, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
