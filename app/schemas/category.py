from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    children: Optional[List['CategoryResponse']] = None
    
    model_config = {"from_attributes": True}


class CategoryWithSupplierCount(CategoryResponse):
    supplier_count: int