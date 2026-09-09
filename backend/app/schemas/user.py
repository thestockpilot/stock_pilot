import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


def principal_out(principal) -> dict:
    """Serialise a signed-in user or admin to the UserOut shape."""
    role = getattr(principal, "role", "user")
    role = role.value if hasattr(role, "value") else role
    return {
        "id": str(principal.id),
        "email": principal.email,
        "full_name": principal.full_name,
        "role": role,
        "is_active": principal.is_active,
        "phone": getattr(principal, "phone", None),
        "bio": getattr(principal, "bio", None),
        "avatar_url": getattr(principal, "avatar_url", None),
        "created_at": principal.created_at.isoformat() if principal.created_at else None,
    }


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    bio: str | None = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
