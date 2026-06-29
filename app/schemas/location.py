from pydantic import BaseModel, Field
from typing import Optional


class LocationBase(BaseModel):
    city: str = Field(..., max_length=100)
    region: Optional[str] = Field(None, max_length=100)


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int

    model_config = {"from_attributes": True}
