from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserNoteBase(BaseModel):
    note_text: str
    note_type: Optional[str] = Field("general", max_length=30)
    rating_impact: int = 0

    @field_validator('note_type')
    @classmethod
    def validate_note_type(cls, v: str) -> str:
        allowed = ['general', 'quality', 'price', 'delivery', 'communication', 'other']
        if v not in allowed:
            raise ValueError(f'note_type must be one of {allowed}')
        return v

    @field_validator('rating_impact')
    @classmethod
    def validate_rating_impact(cls, v: int) -> int:
        if v < -2 or v > 2:
            raise ValueError('rating_impact must be between -2 and 2')
        return v


class UserNoteCreate(UserNoteBase):
    pass


class UserNoteResponse(UserNoteBase):
    id: int
    supplier_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}