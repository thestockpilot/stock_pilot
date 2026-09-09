"""Per-user notification preferences."""
import uuid
from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

DEFAULT_PREFS = {
    "verdict_changes": True,
    "news_sentiment": True,
    "price_alerts": True,
    "marketplace_updates": False,
    "weekly_report": True,
    "product_news": False,
}


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    user_id    : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    prefs      : Mapped[dict]      = mapped_column(JSONB, nullable=False, default=dict)
    updated_at : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
