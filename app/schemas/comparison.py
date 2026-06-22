from pydantic import BaseModel, field_validator
from typing import List

from .supplier import SupplierResponse


class ComparisonRequest(BaseModel):
    supplier_ids: List[int]

    @field_validator('supplier_ids')
    @classmethod
    def validate_supplier_ids(cls, v: List[int]) -> List[int]:
        if len(v) < 2:
            raise ValueError('Need at least 2 suppliers for comparison')
        if len(v) > 5:
            raise ValueError('Maximum 5 suppliers for comparison')
        return v


class ComparisonResponse(BaseModel):
    suppliers: List[SupplierResponse]