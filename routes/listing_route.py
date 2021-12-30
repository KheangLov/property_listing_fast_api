from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from listing import ListingRes, ListingCreate, ListingUpdate
from helper import *
from pony.orm import select, count, desc

router = APIRouter()


@router.get('/listings')
async def get_listings(current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        listings = Model.Listing.select().prefetch(Model.Property)
        result = [ListingRes.from_orm(u) for u in listings]
    return result


@router.get('/listings/front')
async def get_listings_front():
    with db_session:
        listings = select(l for l in Model.Listing if l.status == 'active').prefetch(Model.Property)
        result = [ListingRes.from_orm(u) for u in listings]
    return result


@router.get('/listings/latest')
async def get_listings_latest():
    with db_session:
        listings = select(l for l in Model.Listing).prefetch(Model.Property).order_by(desc(Model.Listing.updated_at))[:10]
        result = [ListingRes.from_orm(u) for u in listings]
    return result


@router.get('/listings_count')
async def get_listings_count():
    with db_session:
        return dict(select((p.status, count(p.id)) for p in Model.Listing))


@router.get('/listings/{id}')
async def get_listing(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        prop = Model.Listing.select().prefetch(Model.Property).prefetch(Model.User)
        return [ListingRes.from_orm(u) for u in prop if u.id == id][0]


@router.get('/listings/front/{id}')
async def get_listing_front(id: int):
    with db_session:
        listings = select(l for l in Model.Listing if l.status == 'active').prefetch(Model.Property).prefetch(Model.User)
        return [ListingRes.from_orm(u) for u in listings if u.id == id][0]


@router.post('/listings', tags=['Listing'])
def create_listing(request: ListingCreate, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        Model.Property[request.property_id].status = 'listing pending'
        request.status = 'inactive'
        request.created_by = current_user.id
        req_dict = request.dict()
        req_dict["property"] = Model.Property[request.property_id]
        del req_dict["property_id"]
        prop = ListingCreate.from_orm(Model.Listing(**req_dict))

        return {
            'success': True,
            'data': jsonable_encoder(prop)
        }


@router.put('/listings/{id}', tags=['Listing'])
@db_session
def update_listing(id: int, request: ListingUpdate, current_user: Model.User = Depends(get_current_active_user)):
    if request.status:
        if request.status == 'active':
            prop = Model.Property[Model.Listing[id].property.id]
            print(prop.status)
            if prop.status != 'listing pending':
                return {
                    'success': False,
                    'message': 'Can not approved this listing!'
                }

            prop.status = 'listing'
            prop.approved_by = current_user.id
            prop.approved_at = datetime.now()
        else:
            Model.Property[Model.Listing[id].property.id].status = 'listing pending'

        Model.Listing[id].status = request.status

    if request.close_reason:
        Model.Listing[id].close_reason = request.close_reason

    Model.Listing[id].updated_by = current_user.id
    Model.Listing[id].updated_at = datetime.now()

    prop = Model.Listing.select()
    return {
        'success': True,
        'data': [ListingUpdate.from_orm(u) for u in prop if u.id == id][0]
    }
