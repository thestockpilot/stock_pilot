"""Per-role subtype tables for the investor and analyst roles."""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.models.user import UserRole


class InvestorProfile(Base):
    __tablename__ = "investors"

    user_id        : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    risk_tolerance : Mapped[str]       = mapped_column(String(20), nullable=False, default="Moderate")
    created_at     : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="investor_profile")


class AnalystProfile(Base):
    __tablename__ = "analysts"

    user_id      : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    is_verified  : Mapped[bool]      = mapped_column(Boolean, nullable=False, default=False)
    payout_email : Mapped[str]       = mapped_column(String(320), nullable=True)
    created_at   : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analyst_profile")


PROFILE_BY_ROLE = {
    UserRole.investor: InvestorProfile,
    UserRole.analyst:  AnalystProfile,
}


def profile_for(role: UserRole, user_id: uuid.UUID):
    """Return a new, unpersisted subtype row for the given user role."""
    model = PROFILE_BY_ROLE.get(role)
    return model(user_id=user_id) if model else None
