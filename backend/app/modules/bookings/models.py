import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ExcludeConstraint, JSONB, TSTZRANGE, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Booking(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bookings"

    booking_reference: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rental_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rental_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rental_type: Mapped[str] = mapped_column(String(30), nullable=False)  # FIXED_DURATION, SUBSCRIPTION
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    booking_period: Mapped[Optional[tuple]] = mapped_column(TSTZRANGE, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default="HELD",
        server_default="HELD",
        nullable=False,
        index=True,
    )
    hold_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_pickup_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_return_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="chk_booking_period_valid",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'HELD', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'EXPIRED')",
            name="chk_booking_status",
        ),
        # PostgreSQL Concurrency Exclusion Constraint preventing overlapping bookings/holds on the same vehicle
        ExcludeConstraint(
            ("vehicle_id", "="),
            ("booking_period", "&&"),
            where="status IN ('HELD', 'CONFIRMED', 'ACTIVE')",
            name="no_overlapping_active_vehicle_bookings",
            using="gist",
        ),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="bookings")
    rental_plan: Mapped["RentalPlan"] = relationship("RentalPlan", back_populates="bookings")
    price_snapshot: Mapped[Optional["BookingPriceSnapshot"]] = relationship(
        "BookingPriceSnapshot", back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="booking")
    deposit: Mapped[Optional["Deposit"]] = relationship("Deposit", back_populates="booking", uselist=False)
    inspections: Mapped[List["Inspection"]] = relationship("Inspection", back_populates="booking")
    settlement_item: Mapped[Optional["SettlementItem"]] = relationship("SettlementItem", back_populates="booking", uselist=False)


class BookingPriceSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "booking_price_snapshots"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    currency: Mapped[str] = mapped_column(String(10), default="INR", server_default="INR", nullable=False)
    base_rate_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_units: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_type: Mapped[str] = mapped_column(String(20), nullable=False)  # HOUR, DAY, MONTH
    base_rental_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mileage_allowance_km: Mapped[int] = mapped_column(Integer, nullable=False)
    excess_mileage_rate_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    security_deposit_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tax_rate_basis_points: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    discount_amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    total_payable_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    snapshot_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "base_rental_amount_minor >= 0 AND tax_amount_minor >= 0 AND security_deposit_minor >= 0 AND total_payable_minor >= 0",
            name="chk_price_snapshot_non_negative",
        ),
    )

    booking: Mapped["Booking"] = relationship("Booking", back_populates="price_snapshot")
