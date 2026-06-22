from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any

from ..models import Supplier, UserNote


def get_notes_by_supplier(db: Session, supplier_id: int) -> List[UserNote]:
    """Получить все заметки о поставщике."""
    return db.query(UserNote).filter(
        UserNote.supplier_id == supplier_id
    ).order_by(desc(UserNote.created_at)).all()


def create_note(db: Session, supplier_id: int, note_data: Dict[str, Any]) -> UserNote:
    """Создать заметку о поставщике."""
    note = UserNote(supplier_id=supplier_id, **note_data)
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Обновляем рейтинг поставщика (если есть влияние)
    if note.rating_impact and note.rating_impact != 0:
        update_supplier_rating(db, supplier_id)
    
    return note


def update_note(db: Session, note_id: int, note_data: Dict[str, Any]) -> Optional[UserNote]:
    """Обновить заметку."""
    note = db.query(UserNote).filter(UserNote.id == note_id).first()
    if not note:
        return None
    
    old_impact = note.rating_impact
    supplier_id = note.supplier_id
    
    for key, value in note_data.items():
        setattr(note, key, value)
    
    db.commit()
    db.refresh(note)
    
    # Если изменился rating_impact - пересчитываем рейтинг
    if 'rating_impact' in note_data and note_data['rating_impact'] != old_impact:
        update_supplier_rating(db, supplier_id)
    
    return note


def delete_note(db: Session, note_id: int) -> bool:
    """Удалить заметку."""
    note = db.query(UserNote).filter(UserNote.id == note_id).first()
    if not note:
        return False
    
    supplier_id = note.supplier_id
    db.delete(note)
    db.commit()
    
    # Пересчитываем рейтинг
    update_supplier_rating(db, supplier_id)
    return True


def update_supplier_rating(db: Session, supplier_id: int) -> None:
    """
    Пересчитать рейтинг поставщика на основе всех заметок с rating_impact.
    База - 3.0 + сумма всех impact / количество заметок.
    """
    notes = db.query(UserNote).filter(
        UserNote.supplier_id == supplier_id,
        UserNote.rating_impact.isnot(None)
    ).all()
    
    if notes:
        total_impact = sum(n.rating_impact for n in notes)
        avg_impact = total_impact / len(notes)
        new_rating = 3.0 + avg_impact
        new_rating = max(0.0, min(5.0, new_rating))  # Ограничиваем 0-5
    else:
        new_rating = 3.0
    
    # Обновляем рейтинг
    db.query(Supplier).filter(Supplier.id == supplier_id).update({
        "rating": round(new_rating, 2),
        "rating_count": len(notes)
    })
    db.commit()
