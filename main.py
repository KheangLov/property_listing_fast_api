from datetime import datetime, date, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pony.orm import *
from decimal import Decimal
import uvicorn

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


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
app = FastAPI()
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


db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9900, reload=True)
