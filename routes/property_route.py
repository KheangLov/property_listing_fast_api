from fastapi import APIRouter
from fastapi import File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from property import PropertyCreate, PropertyUpdate, PropertyRes
from helper import *
# from core import Base64ToFile

security = HTTPBearer()
router = APIRouter()


@router.get('/properties')
async def get_properties(current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        properties = Model.Property.select()
        result = [PropertyRes.from_orm(u) for u in properties]
    return result


@router.get('/properties/{id}')
async def get_property(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        prop = Model.Property.select()
        return [PropertyRes.from_orm(u) for u in prop if u.id == id][0]


@router.post('/properties', tags=['Property'])
def create_property(request: PropertyCreate, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        user_id = request.user_id if request.user_id else current_user.id
        # base64_text_file = Base64ToFile(data)
        # return base64_text_file.filename
        prop = dict(PropertyCreate.from_orm(Model.Property(
            sale_list_price=request.sale_list_price,
            rent_list_price=request.rent_list_price,
            street_no=request.street_no,
            house_no=request.house_no,
            address=request.address,
            full_address=request.full_address,
            latitude=request.latitude,
            longitude=request.longitude,
            land_width=request.land_width,
            land_length=request.land_length,
            land_area=request.land_area,
            description=request.description,
            # image=request.image,
            # gallery=request.gallery,
            is_rent=request.is_rent,
            is_sale=request.is_sale,
            status='pending',
            created_by=current_user.id,
            user_id=user_id,
        )))

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
        Model.Property[id].latitude = request.latitude
    if request.longitude:
        Model.Property[id].longitude = request.longitude
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
    if request.gallery:
        Model.Property[id].gallery = request.gallery
    if request.is_rent:
        Model.Property[id].is_rent = request.is_rent
    if request.is_sale:
        Model.Property[id].is_sale = request.is_sale
    if request.status:
        Model.Property[id].status = request.status
    if request.user_id:
        Model.Property[id].user_id = request.user_id

    Model.Property[id].updated_by = current_user
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
