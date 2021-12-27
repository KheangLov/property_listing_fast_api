from fastapi import APIRouter
from pony.orm import select
from kh_address import KhAddressRes
from helper import *

router = APIRouter()


@router.get('/kh_address')
async def get_addresses(code: str = ''):
    with db_session:
        adds = select(a for a in Model.KhAddress if a.code.startswith(code) and len(a.code) == (len(code) + 2))
        result = [KhAddressRes.from_orm(u) for u in adds]
    return result


@router.get('/kh_address/{code}')
async def get_addresses_by_code(code: str = ''):
    with db_session:
        adds = select(a for a in Model.KhAddress if a.code == code)
        result = [KhAddressRes.from_orm(u) for u in adds]
    return result[0]


@router.get('/kh_address_count')
async def get_kh_address_count():
    with db_session:
        return Model.KhAddress.select().count()