from datetime import timedelta, datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional as TypingOptional
from jose import JWTError, jwt
from pony.orm import db_session
from hash import Hash
from model import Model
from user import *
from token_auth import TokenData

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def find_user(email):
    with db_session:
        user = Model.User.select()
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
