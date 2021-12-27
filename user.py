from pydantic import BaseModel
import pydantic
from typing import Optional as OptionalTyping


class UserRes(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    disabled: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserReg(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str
    disabled: bool

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str
    disabled: bool

    class Config:
        orm_mode = True


class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = OptionalTyping[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(mcs, name, bases, namespaces, **kwargs)


class UpdateUser(UserIn, metaclass=AllOptional):
    pass


class UpdateUserPassword(BaseModel):
    password: str

    class Config:
        orm_mode = True
