from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import pydantic
from property import PropertyRes


class ListingRes(BaseModel):
    id: Optional[int]
    sale_price: Optional[float]
    rent_price: Optional[float]
    property: Optional[PropertyRes]
    close_reason: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    image: Optional[str]
    status: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ListingCreate(BaseModel):
    sale_price: Optional[float]
    rent_price: Optional[float]
    property_id: Optional[int]
    status: Optional[str]
    created_by: Optional[int]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(mcs, name, bases, namespaces, **kwargs)


class ListingUpdate(ListingCreate, metaclass=AllOptional):
    pass
    approved_by: Optional[int]
    close_reason: Optional[str]
    updated_by: int
    updated_at: datetime
