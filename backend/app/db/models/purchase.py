import uuid
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Purchase(Base):
    """A user's purchase of a marketplace strategy listing (mock/demo payment)."""
    __tablename__ = "purchases"
    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_purchase_user_listing"),
    )

    id             : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id     : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("marketplace_listings.id", ondelete="CASCADE"), nullable=False)
    price_cents    : Mapped[int]       = mapped_column(Integer, nullable=False, default=0)
    payment_method : Mapped[str]       = mapped_column(String(60), nullable=True)
    created_at     : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
