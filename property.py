from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import pydantic
from user import UserRes


class PropertyRes(BaseModel):
    id: int
    sale_list_price: Optional[float]
    rent_list_price: Optional[float]
    street_no: str
    house_no: str
    address: str
    full_address: str
    latitude: float
    longitude: float
    land_width: float
    land_length: float
    land_area: float
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    image: Optional[str]
    is_rent: Optional[bool]
    is_sale: Optional[bool]
    status: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    reason: Optional[str]
    user: UserRes

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PropertyCreate(BaseModel):
    sale_list_price: Optional[float]
    rent_list_price: Optional[float]
    street_no: str
    house_no: str
    address: str
    full_address: str
    latitude: str
    longitude: str
    land_width: float
    land_length: float
    land_area: float
    description: Optional[str]
    image: Optional[str]
    is_rent: Optional[bool]
    is_sale: Optional[bool]
    status: Optional[str] = 'pending'
    created_by: Optional[int]
    updated_by: Optional[int]
    user_id: Optional[int]

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


class PropertyUpdate(PropertyCreate, metaclass=AllOptional):
    pass
    reason: Optional[str]
