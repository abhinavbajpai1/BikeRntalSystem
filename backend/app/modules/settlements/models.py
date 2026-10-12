import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Settlement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "settlements"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    settlement_reference: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    gross_rental_amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    commission_deducted_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    adjustments_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    net_payable_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default="DRAFT",
        server_default="DRAFT",
        nullable=False,
        index=True,
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'APPROVED', 'PROCESSED', 'FAILED')",
            name="chk_settlement_status",
        ),
        CheckConstraint(
            "period_end >= period_start",
            name="chk_settlement_period_valid",
        ),
    )

    # Relationships
    partner: Mapped["Partner"] = relationship("Partner", back_populates="settlements")
    items: Mapped[List["SettlementItem"]] = relationship("SettlementItem", back_populates="settlement", cascade="all, delete-orphan")
    payout_attempts: Mapped[List["PayoutAttempt"]] = relationship("PayoutAttempt", back_populates="settlement", cascade="all, delete-orphan")


class SettlementItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "settlement_items"

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        unique=True,  # Crucial invariant: A booking can belong to at most one settlement
        nullable=False,
        index=True,
    )
    gross_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    commission_rate_basis_points: Mapped[int] = mapped_column(Integer, nullable=False)
    commission_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    net_partner_share_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "commission_rate_basis_points >= 0 AND commission_rate_basis_points <= 10000",
            name="chk_item_commission_basis_points",
        ),
        CheckConstraint(
            "gross_amount_minor >= 0 AND commission_amount_minor >= 0 AND net_partner_share_minor >= 0",
            name="chk_item_amounts_non_negative",
        ),
    )

    settlement: Mapped["Settlement"] = relationship("Settlement", back_populates="items")
    booking: Mapped["Booking"] = relationship("Booking", back_populates="settlement_item")


class PayoutAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payout_attempts"

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="INITIATED", server_default="INITIATED", nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "amount_minor > 0",
            name="chk_payout_amount_positive",
        ),
        CheckConstraint(
            "status IN ('INITIATED', 'SUCCEEDED', 'FAILED')",
            name="chk_payout_status",
        ),
    )

    settlement: Mapped["Settlement"] = relationship("Settlement", back_populates="payout_attempts")
