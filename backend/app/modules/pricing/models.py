import uuid
from typing import List, Optional
from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RentalPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "rental_plans"

    city_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    rental_type: Mapped[str] = mapped_column(String(30), nullable=False)  # FIXED_DURATION, SUBSCRIPTION
    tier: Mapped[str] = mapped_column(String(30), nullable=False)  # ECONOMY, COMFORT, PREMIUM
    min_duration_hours: Mapped[int] = mapped_column(Integer, default=24, server_default="24", nullable=False)
    max_duration_hours: Mapped[int] = mapped_column(Integer, default=720, server_default="720", nullable=False)
    base_rate_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)  # in paise
    rate_unit: Mapped[str] = mapped_column(String(20), default="DAY", server_default="DAY", nullable=False)  # HOUR, DAY, MONTH
    mileage_allowance_km_per_day: Mapped[int] = mapped_column(Integer, default=200, server_default="200", nullable=False)
    excess_mileage_rate_minor: Mapped[int] = mapped_column(BigInteger, default=1200, server_default="1200", nullable=False)  # ₹12/km
    security_deposit_minor: Mapped[int] = mapped_column(BigInteger, default=300000, server_default="300000", nullable=False)  # ₹3,000
    tax_rate_basis_points: Mapped[int] = mapped_column(Integer, default=1800, server_default="1800", nullable=False)  # 18.00%
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "rental_type IN ('FIXED_DURATION', 'SUBSCRIPTION')",
            name="chk_rental_plan_type",
        ),
        CheckConstraint(
            "tier IN ('ECONOMY', 'COMFORT', 'PREMIUM')",
            name="chk_rental_plan_tier",
        ),
        CheckConstraint(
            "rate_unit IN ('HOUR', 'DAY', 'MONTH')",
            name="chk_rental_plan_rate_unit",
        ),
        CheckConstraint(
            "base_rate_minor >= 0 AND security_deposit_minor >= 0 AND excess_mileage_rate_minor >= 0",
            name="chk_rental_plan_monetary_positive",
        ),
        CheckConstraint(
            "min_duration_hours > 0 AND max_duration_hours >= min_duration_hours",
            name="chk_rental_plan_durations",
        ),
    )

    # Relationships
    city: Mapped[Optional["City"]] = relationship("City")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="rental_plan")
