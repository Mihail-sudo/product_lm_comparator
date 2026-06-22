from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


class CertificateBase(BaseModel):
    certificate_name: str = Field(..., max_length=255)
    certificate_type: Optional[str] = Field(None, max_length=50)
    issuing_authority: Optional[str] = Field(None, max_length=255)
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None
    file_url: Optional[str] = Field(None, max_length=255)
    is_valid: bool = True

    @field_validator('certificate_type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ['quality', 'safety', 'organic', 'halal', 'kosher', 'iso', 'other']
        if v not in allowed:
            raise ValueError(f'certificate_type must be one of {allowed}')
        return v


class CertificateCreate(CertificateBase):
    pass


class CertificateResponse(CertificateBase):
    id: int
    supplier_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}