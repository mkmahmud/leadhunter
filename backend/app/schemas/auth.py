from typing import Literal

from pydantic import BaseModel


UserRole = Literal["admin", "viewer"]


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: UserRole = "viewer"
