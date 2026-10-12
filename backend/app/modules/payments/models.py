import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", server_default="INR", nullable=False)
    payment_type: Mapped[str] = mapped_column(
        String(30),
        default="RENTAL_FEE",
        server_default="RENTAL_FEE",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        server_default="PENDING",
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), default="MOCK_PROVIDER", server_default="MOCK_PROVIDER", nullable=False)
    provider_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "amount_minor > 0",
            name="chk_payment_amount_positive",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'REFUNDED')",
            name="chk_payment_status",
        ),
        CheckConstraint(
            "payment_type IN ('RENTAL_FEE', 'SECURITY_DEPOSIT', 'EXCESS_MILEAGE', 'DAMAGE_FEE')",
            name="chk_payment_type",
        ),
    )

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="payments")
    events: Mapped[List["PaymentEvent"]] = relationship("PaymentEvent", back_populates="payment", cascade="all, delete-orphan")
    refunds: Mapped[List["Refund"]] = relationship("Refund", back_populates="payment")


class PaymentEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payment_events"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    payment: Mapped["Payment"] = relationship("Payment", back_populates="events")


class Refund(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "refunds"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", server_default="PENDING", nullable=False)
    provider_refund_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "amount_minor > 0",
            name="chk_refund_amount_positive",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'SUCCEEDED', 'FAILED')",
            name="chk_refund_status",
        ),
    )

    payment: Mapped["Payment"] = relationship("Payment", back_populates="refunds")


class Deposit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "deposits"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING_COLLECTION",
        server_default="PENDING_COLLECTION",
        nullable=False,
    )
    deducted_amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    refunded_amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    deduction_reason: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "amount_minor >= 0 AND deducted_amount_minor >= 0 AND refunded_amount_minor >= 0",
            name="chk_deposit_amounts_positive",
        ),
        CheckConstraint(
            "status IN ('PENDING_COLLECTION', 'HELD', 'REFUNDED_FULL', 'REFUNDED_PARTIAL', 'DEDUCTED')",
            name="chk_deposit_status",
        ),
    )

    booking: Mapped["Booking"] = relationship("Booking", back_populates="deposit")
