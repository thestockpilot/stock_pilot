from typing import Literal
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    # Self-registration is limited to investor and analyst. "admin" is
    # deliberately excluded — an admin can only be promoted by another admin,
    # so a Literal here rejects any admin attempt with an automatic 422.
    role: Literal["investor", "analyst"] = "investor"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict | None = None
