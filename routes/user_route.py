from fastapi import APIRouter, Security, File, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from token_auth import Token
from helper import *

security = HTTPBearer()
router = APIRouter()


@router.get('/current-user')
async def get_current_user(current_user: Model.User = Depends(get_current_active_user), credentials: HTTPAuthorizationCredentials = Security(security)):
    current_user = dict(current_user)
    current_user['access_token'] = credentials.credentials
    return current_user


@router.get('/users')
async def get_users(current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        user = Model.User.select()
        result = [UserRes.from_orm(u) for u in user]
    return result


@router.get('/users/{id}')
async def get_user(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        user = Model.User.select()
        return [UserRes.from_orm(u) for u in user if u.id == id][0]


@router.post('/register', tags=['User'])
def register(request: UserIn):
    with db_session:
        _hash = Hash()
        password = _hash.get_password_hash(request.password)

        # try:
        user = dict(UserIn.from_orm(Model.User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=password,
            phone=request.phone,
        )))

        del user['password']

        return {
            'success': True,
            'data': jsonable_encoder(user)
        }
        # except ValidationError as e:
        #     print(e)
        #     return {
        #         'success': False,
        #         'data': e
        #     }


@router.post("/upload_profile", tags=['User'])
def update_profile(file: UploadFile = File(...)):
    return {"file_size": file}


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin):
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@router.put('/users/{id}', tags=['User'])
@db_session
def update_user(id: int, request: UpdateUser, current_user: Model.User = Depends(get_current_active_user)):
    if request.first_name:
        Model.User[id].first_name = request.first_name
    if request.last_name:
        Model.User[id].last_name = request.last_name
    if request.email:
        Model.User[id].email = request.email
    if request.phone:
        Model.User[id].phone = request.phone
    if request.disabled:
        Model.User[id].disabled = request.disabled

    Model.User[id].updated_at = datetime.now()

    user = Model.User.select()
    return {
        'success': True,
        'data': [UserRes.from_orm(u) for u in user if u.id == id][0]
    }


@router.put('/change_password/{id}', tags=['User'])
@db_session
def update_user_password(id: int, request: UpdateUserPassword, current_user: Model.User = Depends(get_current_active_user)):
    if request.password:
        Model.User[id].password = request.password
    user = Model.User.select()
    return [UserRes.from_orm(u) for u in user if u.id == id]


@router.delete('/users/{id}', tags=['User'])
def delete_user(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        user = Model.User.select(lambda u: u.id == id)
        user.delete()
        return {
            'message': 'Delete successfully'
        }


# @router.get("/logout")
# def logout(response: Response):
#     response.delete_cookie(key='access_token')
#     return response
