from datetime import datetime, date, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator, ValidationError, EmailStr
from pony.orm import *
from decimal import Decimal
import uvicorn
from starlette.requests import Request
from hash import Hash
from typing import Optional as TypingOptional
from fastapi.middleware.cors import CORSMiddleware
import pydantic
from typing import Optional as OptionalTyping

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

db = Database()
db.bind(provider='postgres', user='macbook', password='', host='127.0.0.1', database='prop_listing')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    phone: str = None


class User(db.Entity):
    _table_ = "users"
    id = PrimaryKey(int, auto=True)
    first_name = Optional(str)
    last_name = Optional(str)
    email = Required(str, unique=True)
    phone = Required(str)
    password = Required(str)
    disabled = Optional(bool, default=0)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Required(datetime, default=lambda: datetime.now())
    property_created_by = Set('Property', reverse='created_by')
    property_updated_by = Set('Property', reverse='updated_by')
    property_user = Set('Property', reverse='user_id')
    listing_created_by = Set('Listing', reverse='created_by')
    listing_updated_by = Set('Listing', reverse='updated_by')
    listing_approved_by = Set('Listing', reverse='approved_by')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserRes(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    disabled: bool

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str
    disabled: bool

    # @validator('email')
    # def unique_email(cls: BaseModel, v: EmailStr) -> EmailStr:
    #     with db_session:
    #         users = User.select()
    #     if str(v) in set(map(lambda u: u.email, users)):
    #         raise ValueError('Email already in use.')
    #     return v

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


class Property(db.Entity):
    _table_ = "properties"
    id = PrimaryKey(int, auto=True)
    sale_list_price = Optional(Decimal)
    sale_list_price_date = Optional(date)
    sold_price = Optional(Decimal)
    sold_price_date = Optional(date)
    street_no = Optional(str)
    house_no = Optional(str)
    address = Required(str)
    full_address = Optional(str)
    latitude = Required(Decimal)
    longitude = Required(Decimal)
    land_width = Required(Decimal)
    land_length = Required(Decimal)
    land_area = Required(Decimal)
    description = Optional(str)
    record_type = Required(str)
    zone_type = Optional(str)
    land_shape_type = Optional(str)
    site_position = Optional(str)
    facing_type = Optional(str)
    tenure_type = Optional(str)
    label_type = Optional(str)
    type = Required(str)
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Required(datetime, default=lambda: datetime.now())
    deleted_at = Optional(datetime)
    image = Optional(str)
    gallery = Optional(str)
    is_rent = Optional(bool, default='f')
    is_sale = Optional(bool, default='f')
    shape = Optional(str)
    current_use = Optional(str)
    topography = Optional(str)
    status = Optional(str)
    created_by = Required(User, reverse='property_created_by')
    updated_by = Optional(User, reverse='property_updated_by')
    user_id = Optional(User, reverse='property_user')
    listings = Set('Listing')


class Listing(db.Entity):
    _table_ = "listings"
    id = PrimaryKey(int, auto=True)
    property_id = Required(Property)
    exclusive_date = Optional(date)
    created_by = Required(User, reverse='listing_created_by')
    updated_by = Optional(User, reverse='listing_updated_by')
    sale_list_price = Optional(Decimal)
    sold_price = Optional(Decimal)
    sold_price_date = Optional(date)
    rent_list_price = Optional(Decimal)
    rented_price = Optional(Decimal)
    rented_price_date = Optional(date)
    status = Optional(str)
    additional_items = Optional(LongStr)
    is_rent = Optional(bool, default='f')
    is_sale = Optional(bool, default='f')
    close_reason = Optional(str)
    created_at = Optional(datetime, default=lambda: datetime.now())
    updated_at = Optional(datetime, default=lambda: datetime.now())
    deleted_at = Optional(datetime, default=lambda: datetime.now())
    approved_at = Optional(datetime)
    approved_by = Optional(User, reverse='listing_approved_by')


class TokenData(BaseModel):
    email: TypingOptional[str] = None


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
#
# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return User(**user_dict)
#
#
# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
#
#
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
#
#
# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(fake_users_db, form_data.phone, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}
#
#
# @app.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


def find_user(email):
    with db_session:
        user = User.select()
        result = [UserIn.from_orm(u) for u in user if u.email == email]
    return result[0]


def authenticate_user(email: str, password: str):
    _hash = Hash()
    user = find_user(email)
    if not user:
        return False
    if not _hash.verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: TypingOptional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = find_user(token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserIn = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


security = HTTPBearer()


@app.get('/current-user')
async def get_current_user(current_user: User = Depends(get_current_active_user), credentials:
HTTPAuthorizationCredentials = Security(security)):
    current_user = dict(current_user)
    current_user['access_token'] = credentials.credentials
    return current_user


@app.get('/users')
async def get_users(current_user: User = Depends(get_current_active_user)):
    with db_session:
        user = User.select()
        result = [UserRes.from_orm(u) for u in user]
    return result


@app.post('/register', tags=['User'])
def register(request: UserIn, current_user: User = Depends(get_current_active_user)):
    with db_session:
        _hash = Hash()
        password = _hash.get_password_hash(request.password)

        # try:
        user = dict(UserIn.from_orm(User(
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


@app.post("/login", response_model=Token)
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


@app.put('/users/{id}', tags=['User'])
@db_session
def update_user(id: int, request: UpdateUser, current_user: User = Depends(get_current_active_user)):
    if request.first_name:
        User[id].first_name = request.first_name
    if request.last_name:
        User[id].last_name = request.last_name
    if request.email:
        User[id].email = request.email
    if request.phone:
        User[id].phone = request.phone
    if request.disabled:
        User[id].disabled = request.disabled
    user = User.select()
    return [UserRes.from_orm(u) for u in user if u.id == id]


@app.delete('/users/{id}', tags=['User'])
def delete_user(id: int, current_user: User = Depends(get_current_active_user)):
    with db_session:
        user = User.select(lambda u: u.id == id)
        user.delete()
        return {
            'message': 'Delete successfully'
        }


# create_tables=True
db.generate_mapping()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9900, reload=True)
