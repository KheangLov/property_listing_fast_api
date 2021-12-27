from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from listing import ListingRes, ListingCreate, ListingUpdate
from helper import *
from base64_to_file import Base64ToFile
from pony.orm import select

router = APIRouter()


@router.get('/listings')
async def get_listings(current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        listings = Model.Listing.select()
        result = [ListingRes.from_orm(u) for u in listings]
    return result


@router.get('/listings/front')
async def get_listings_front():
    with db_session:
        listings = select(l for l in Model.Listing if l.status == 'active')
        result = [ListingRes.from_orm(u) for u in listings]
    return result


@router.get('/listings_count')
async def get_listings_count():
    with db_session:
        return Model.Listing.select().count()


@router.get('/listings/{id}')
async def get_listing(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        prop = Model.Listing.select()
        return [ListingRes.from_orm(u) for u in prop if u.id == id][0]


@router.get('/listings/front/{id}')
async def get_listing_front(id: int):
    with db_session:
        listings = select(l for l in Model.Listing if l.status == 'active')
        return [ListingRes.from_orm(u) for u in listings if u.id == id][0]


@router.post('/listings', tags=['Listing'])
def create_listing(request: ListingCreate, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        base64_text_file = ''
        if request.image:
            base64_text_file = Base64ToFile(request.image)
        prop = dict(ListingCreate.from_orm(Model.Listing(
            sale_price=request.sale_price,
            rent_price=request.rent_price,
            property_id=request.property_id,
            # close_reason=request.close_reason,
            image=base64_text_file.filename if base64_text_file and base64_text_file.filename else base64_text_file,
            status='inactive',
            created_by=current_user.id,
        )))

        return {
            'success': True,
            'data': jsonable_encoder(prop)
        }


@router.put('/listings/{id}', tags=['Listing'])
@db_session
def update_listing(id: int, request: ListingUpdate, current_user: Model.User = Depends(get_current_active_user)):
    if request.status:
        Model.Listing[id].status = request.status
    if request.approved_by:
        Model.Listing[id].approved_by = current_user.id
        Model.Listing[id].approved_at = datetime.now()
    if request.close_reason:
        Model.Listing[id].close_reason = request.close_reason

    Model.Listing[id].updated_by = current_user.id
    Model.Listing[id].updated_at = datetime.now()

    prop = Model.Listing.select()
    return {
        'success': True,
        'data': [ListingUpdate.from_orm(u) for u in prop if u.id == id][0]
    }
