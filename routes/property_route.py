from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from property import PropertyCreate, PropertyUpdate, PropertyRes
from listing import ListingRes
from helper import *
from base64_to_file import Base64ToFile
from pony.orm import select, count, desc
from fastapi_pagination import paginate, Page

router = APIRouter()


# current_user: Model.User = Depends(get_current_active_user)
@router.get('/properties', response_model=Page[PropertyRes])
async def get_properties():
    with db_session:
        return paginate(list(Model.Property.select().prefetch(Model.User).order_by(desc(Model.Property.updated_at))))
        # return {
        #     'current_page': page,
        #     'data': list(PropertyRes(**props.page(page, per_page))),
        #     'per_page': per_page,
        #     'total': props.count(),
        #     'last_page': props.count()//per_page
        # }


@router.get('/properties_count')
async def get_properties_count():
    with db_session:
        return dict(select((p.status, count(p.id)) for p in Model.Property))


@router.get('/properties/latest')
async def get_listings_latest():
    with db_session:
        listings = select(l for l in Model.Property).prefetch(Model.User).order_by(desc(Model.Property.updated_at))[:10]
        result = [PropertyRes.from_orm(u) for u in listings]
    return result


@router.get('/properties/{id}')
async def get_property(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        return PropertyRes.from_orm(Model.Property.get(id=id))


@router.get('/properties/front/{id}')
async def get_property_front(id: int):
    with db_session:
        return PropertyRes.from_orm(Model.Property.get(id=id))


@router.post('/properties', tags=['Property'])
def create_property(request: PropertyCreate, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        user_id = request.user_id if request.user_id else current_user.id
        base64_text_file = ''
        if request.image:
            base64_text_file = Base64ToFile(request.image)

        request.image = f"images/{base64_text_file.filename}"
        request.created_by = current_user.id
        req_dict = request.dict()
        req_dict["user"] = Model.User[user_id]
        del req_dict["user_id"]
        prop = PropertyCreate.from_orm(Model.Property(**req_dict))

        return {
            'success': True,
            'data': jsonable_encoder(prop)
        }


@router.put('/properties/{id}', tags=['Property'])
@db_session
def update_property(id: int, request: PropertyUpdate, current_user: Model.User = Depends(get_current_active_user)):
    if request.sale_list_price:
        Model.Property[id].sale_list_price = request.sale_list_price
    if request.rent_list_price:
        Model.Property[id].rent_list_price = request.rent_list_price
    if request.street_no:
        Model.Property[id].street_no = request.street_no
    if request.house_no:
        Model.Property[id].house_no = request.house_no
    if request.address:
        Model.Property[id].address = request.address
    if request.full_address:
        Model.Property[id].full_address = request.full_address
    if request.latitude:
        Model.Property[id].latitude = str(request.latitude)
    if request.longitude:
        Model.Property[id].longitude = str(request.longitude)
    if request.land_width:
        Model.Property[id].land_width = request.land_width
    if request.land_length:
        Model.Property[id].land_length = request.land_length
    if request.land_area:
        Model.Property[id].land_area = request.land_area
    if request.description:
        Model.Property[id].description = request.description
    if request.image:
        Model.Property[id].image = request.image
    if request.is_rent:
        Model.Property[id].is_rent = request.is_rent
    if request.is_sale:
        Model.Property[id].is_sale = request.is_sale
    if request.reason:
        Model.Property[id].reason = request.reason
    if request.status:
        listing = ListingRes.from_orm(Model.Listing.select(property=Model.Property[id]).first())
        if listing.id and request.status != 'reject':
            Model.Property[id].status = 'listing pending'
        else:
            Model.Property[id].status = request.status
    else:
        Model.Property[id].status = 'pending'
    if request.user_id:
        Model.Property[id].user_id = request.user_id
    if request.image and 'base64,' in request.image:
        base64_text_file = ''
        if request.image:
            base64_text_file = Base64ToFile(request.image)

        request.image = f"images/{base64_text_file.filename}"

    Model.Property[id].updated_by = current_user.id
    Model.Property[id].updated_at = datetime.now()

    prop = Model.Property.select()
    return {
        'success': True,
        'data': [PropertyUpdate.from_orm(u) for u in prop if u.id == id][0]
    }


@router.delete('/properties/{id}', tags=['Property'])
def delete_user(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        prop = Model.Property.select(lambda u: u.id == id)
        prop.delete()
        return {
            'message': 'Delete successfully'
        }
