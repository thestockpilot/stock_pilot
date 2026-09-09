import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.db.models.notification import Notification
from app.db.models.notification_pref import NotificationPreference, DEFAULT_PREFS
from app.schemas.notification import NotificationOut
from app.core.dependencies import get_current_principal, get_current_user, is_admin

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(db: AsyncSession = Depends(get_db), principal = Depends(get_current_principal)):
    if is_admin(principal):
        return []
    result = await db.execute(
        select(Notification).where(Notification.user_id == principal.id).order_by(Notification.created_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.put("/{notification_id}/read")
async def mark_read(notification_id: uuid.UUID, db: AsyncSession = Depends(get_db), principal = Depends(get_current_principal)):
    if is_admin(principal):
        return {"ok": True}
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == principal.id)
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    return {"ok": True}


@router.put("/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db), principal = Depends(get_current_principal)):
    if is_admin(principal):
        return {"ok": True}
    await db.execute(
        update(Notification).where(Notification.user_id == principal.id, Notification.is_read == False).values(is_read=True)
    )
    return {"ok": True}


@router.get("/preferences")
async def get_preferences(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = (await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user.id)
    )).scalar_one_or_none()
    return {**DEFAULT_PREFS, **(row.prefs if row else {})}


@router.put("/preferences")
async def update_preferences(prefs: dict, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    clean = {k: bool(prefs.get(k, DEFAULT_PREFS[k])) for k in DEFAULT_PREFS}
    row = (await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user.id)
    )).scalar_one_or_none()
    if row is None:
        db.add(NotificationPreference(user_id=user.id, prefs=clean))
    else:
        row.prefs = clean
    await db.flush()
    return clean
