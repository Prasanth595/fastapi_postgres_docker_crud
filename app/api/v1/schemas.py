from typing import Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ItemRead(ItemBase):
    id: int

    class Config:
        # Pydantic v2 key instead of orm_mode
        from_attributes = True