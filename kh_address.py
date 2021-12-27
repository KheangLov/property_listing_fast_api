from pydantic import BaseModel


class KhAddressRes(BaseModel):
    code: str
    name_en: str
    path_en: str

    class Config:
        orm_mode = True
