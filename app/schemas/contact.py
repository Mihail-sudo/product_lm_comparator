from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ContactBase(BaseModel):
    contact_type: str = Field(..., max_length=30)
    contact_value: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    is_primary: bool = False

    @field_validator('contact_type')
    @classmethod
    def validate_contact_type(cls, v: str) -> str:
        allowed = ['phone', 'email', 'telegram', 'whatsapp', 'viber', 'other']
        if v not in allowed:
            raise ValueError(f'contact_type must be one of {allowed}')
        return v


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    supplier_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}