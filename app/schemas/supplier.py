from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .category import CategoryResponse
from .contact import ContactResponse
from .order_condition import OrderConditionResponse
from .certificate import CertificateResponse
from .user_note import UserNoteResponse
from .location import LocationResponse, LocationCreate


class SupplierBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    foundation_year: Optional[int] = Field(None, ge=1900)
    is_verified: bool = False
    status: str = "active"

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ['active', 'inactive', 'blocked']:
            raise ValueError('status must be active, inactive or blocked')
        return v


class SupplierCreate(SupplierBase):
    category_ids: Optional[List[int]] = None
    locations: Optional[List[LocationCreate]] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    foundation_year: Optional[int] = Field(None, ge=1900)
    is_verified: Optional[bool] = None
    status: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ['active', 'inactive', 'blocked']:
            raise ValueError('status must be active, inactive or blocked')
        return v


class SupplierResponse(SupplierBase):
    id: int
    rating: Decimal
    rating_count: int
    created_at: datetime
    updated_at: datetime
    
    categories: Optional[List[CategoryResponse]] = None
    contacts: Optional[List[ContactResponse]] = None
    order_conditions: Optional[List[OrderConditionResponse]] = None
    certificates: Optional[List[CertificateResponse]] = None
    notes: Optional[List[UserNoteResponse]] = None
    locations: Optional[List[LocationResponse]] = None
    
    model_config = {"from_attributes": True}


class SupplierListResponse(BaseModel):
    total: int
    items: List[SupplierResponse]
    skip: int
    limit: int


class SupplierSearchParams(BaseModel):
    query_text: Optional[str] = None
    category_id: Optional[int] = None
    city: Optional[str] = None
    region: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    has_certificates: Optional[bool] = None
    min_order_max: Optional[float] = None
    skip: int = 0
    limit: int = 50


class ParseFromUrlRequest(BaseModel):
    url: str
    model: Optional[str] = None