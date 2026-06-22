from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class OrderConditionBase(BaseModel):
    category_id: Optional[int] = None
    min_order_quantity: Optional[Decimal] = None
    min_order_unit: Optional[str] = Field(None, max_length=30)
    price_per_unit: Optional[Decimal] = None
    price_currency: str = "RUB"
    price_negotiable: bool = True
    delivery_terms: Optional[str] = None
    delivery_region: Optional[str] = Field(None, max_length=100)
    delivery_cost: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    lead_time_days: Optional[int] = None

    @field_validator('min_order_unit')
    @classmethod
    def validate_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ['kg', 'ton', 'piece', 'box', 'pallet', 'liter', 'other']
        if v not in allowed:
            raise ValueError(f'min_order_unit must be one of {allowed}')
        return v


class OrderConditionCreate(OrderConditionBase):
    pass


class OrderConditionResponse(OrderConditionBase):
    id: int
    supplier_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}