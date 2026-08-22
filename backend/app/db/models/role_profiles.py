"""Per-role subtype tables (joined-table inheritance).

The shared identity and authentication data stays on the `users` table. Each
role additionally owns a 1:1 subtype row keyed by the same user id, so users are
physically separated by role into `investors`, `analysts` and `admins` without
disturbing authentication or the foreign keys that point at users.id.

The user's `role` column on `users` remains the discriminator, so login, JWT and
require_role() are unchanged; these tables only add role-specific attributes.
"""
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


class AdminProfile(Base):
    __tablename__ = "admins"

    user_id    : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    is_super   : Mapped[bool]      = mapped_column(Boolean, nullable=False, default=False)
    created_at : Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="admin_profile")


# Map each role to its subtype table, so the profile row can be kept in sync
# from a single place on registration and on role change.
PROFILE_BY_ROLE = {
    UserRole.investor: InvestorProfile,
    UserRole.analyst:  AnalystProfile,
    UserRole.admin:    AdminProfile,
}


def profile_for(role: UserRole, user_id: uuid.UUID):
    """Return a new, unpersisted subtype row for the given role."""
    return PROFILE_BY_ROLE[role](user_id=user_id)
