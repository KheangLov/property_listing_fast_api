from fastapi import APIRouter, Security, File, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from token_auth import Token
from helper import *
from base64_to_file import Base64ToFile
from os import getenv
from pony.orm import select, count, desc
from fastapi_pagination import paginate, Page
from typing import Optional

security = HTTPBearer()
router = APIRouter()


@router.get('/current-user')
async def get_current_user(current_user: Model.User = Depends(get_current_active_user), credentials: HTTPAuthorizationCredentials = Security(security)):
    current_user = dict(current_user)
    current_user['profile'] = f"{getenv('URL', 'http://127.0.0.1:9800/')}{current_user['profile']}" if current_user['profile'] else ''
    current_user['access_token'] = credentials.credentials
    return current_user


@router.get('/all_users')
async def get_users(current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        users = Model.User.select()
        result = []
        for u in users:
            user = UserRes.from_orm(u)
            user.profile = f"{getenv('URL', 'http://127.0.0.1:9800/')}{user.profile}" if user.profile else ''
            result.append(user)
    return result


@router.get('/users', response_model=Page[UserRes])
async def get_users(search: Optional[str] = '', current_user: Model.User = Depends(get_current_active_user)):
    if search:
        return paginate(list(Model.User.select().filter(lambda p: str(search) in str(p.first_name) or str(search) in str(p.last_name) or str(search) in str(p.email)).order_by(desc(Model.User.updated_at))))
    return paginate(list(Model.User.select().order_by(desc(Model.User.updated_at))))
    # with db_session:
    #     users = Model.User.select()
    #     result = []
    #     for u in users:
    #         user = UserRes.from_orm(u)
    #         user.profile = f"{getenv('URL', 'http://127.0.0.1:9800/')}{user.profile}" if user.profile else ''
    #         result.append(user)
    # return result


@router.get('/users_count')
async def get_users_count():
    with db_session:
        return dict(select((p.disabled, count(p.id)) for p in Model.User))


@router.get('/users/{id}')
async def get_user(id: int, current_user: Model.User = Depends(get_current_active_user)):
    with db_session:
        user = dict(UserRes.from_orm(Model.User.get(id=id)))
        user['profile'] = f"{getenv('URL', 'http://127.0.0.1:9800/')}{user['profile']}" if user['profile'] else ''
        return user


@router.get('/users/front/{id}')
async def get_user_front(id: int):
    with db_session:
        user = dict(UserRes.from_orm(Model.User.get(id=id)))
        user['profile'] = f"{getenv('URL', 'http://127.0.0.1:9800/')}{user['profile']}" if user['profile'] else ''
        return user


@router.post('/register', tags=['User'])
def register(request: UserReg):
    with db_session:
        _hash = Hash()
        password = _hash.get_password_hash(request.password)
        base64_text_file = ''
        if request.profile:
            base64_text_file = Base64ToFile(request.profile.split('base64,')[1])

        user = find_user(request.email)
        if user:
            return {
                'success': False,
                'message': 'Email already exist!',
                'field': {
                    'email': ['Email already exist!']
                }
            }

        user = dict(UserReg.from_orm(Model.User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=password,
            phone=request.phone,
            profile=f"images/{base64_text_file.filename}" if base64_text_file else ''
        )))

        del user['password']

        return {
            'success': True,
            'data': jsonable_encoder(user)
        }


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
    if hasattr(request, 'disabled'):
        Model.User[id].disabled = request.disabled
    if request.profile and 'base64,' in request.profile:
        Model.User[id].profile = f"images/{Base64ToFile(request.profile.split('base64,')[1]).filename}"

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
        _hash = Hash()
        Model.User[id].password = _hash.get_password_hash(request.password)
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


@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(key='access_token')
    return response
