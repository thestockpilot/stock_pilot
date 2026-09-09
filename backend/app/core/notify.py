"""Helper for creating in-app notifications."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.notification import Notification, NotificationKind


async def notify(db: AsyncSession, user_id, kind: NotificationKind, title: str, body: str | None = None):
    db.add(Notification(user_id=user_id, kind=kind, title=title, body=body))
