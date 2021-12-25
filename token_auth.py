from pydantic import BaseModel
from typing import Optional as TypingOptional


class TokenData(BaseModel):
    email: TypingOptional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
