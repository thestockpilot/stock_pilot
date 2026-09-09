from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.db.models.admin import Admin
from app.db.models.role_profiles import profile_for
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse
from app.schemas.user import principal_out
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user is not None and verify_password(body.password, user.password_hash):
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is suspended")
        return TokenResponse(
            access_token=create_access_token(str(user.id), actor="user"),
            refresh_token=create_refresh_token(str(user.id), actor="user"),
            user=principal_out(user),
        )

    result = await db.execute(select(Admin).where(Admin.email == body.email))
    admin = result.scalar_one_or_none()
    if admin is not None and admin.is_active and verify_password(body.password, admin.password_hash):
        return TokenResponse(
            access_token=create_access_token(str(admin.id), actor="admin"),
            refresh_token=create_refresh_token(str(admin.id), actor="admin"),
            user=principal_out(admin),
        )

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=UserRole(body.role),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    profile = profile_for(user.role, user.id)
    if profile is not None:
        db.add(profile)
    from app.core.notify import notify
    from app.db.models.notification import NotificationKind
    await notify(db, user.id, NotificationKind.system,
                 "Welcome to StockPilot",
                 "Your account is ready. Head to the Advisor to analyse your first stock.")
    await db.flush()
    access = create_access_token(str(user.id), actor="user")
    refresh = create_refresh_token(str(user.id), actor="user")
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=principal_out(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    import uuid
    actor = payload.get("actor", "user")
    subject_id = uuid.UUID(payload["sub"])
    if actor == "admin":
        result = await db.execute(select(Admin).where(Admin.id == subject_id))
        admin = result.scalar_one_or_none()
        if admin is None or not admin.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
        return TokenResponse(
            access_token=create_access_token(str(admin.id), actor="admin"),
            refresh_token=create_refresh_token(str(admin.id), actor="admin"),
        )
    result = await db.execute(select(User).where(User.id == subject_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return TokenResponse(
        access_token=create_access_token(str(user.id), actor="user"),
        refresh_token=create_refresh_token(str(user.id), actor="user"),
    )
