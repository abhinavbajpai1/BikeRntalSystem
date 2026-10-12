import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Inspection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "inspections"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    inspector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    inspection_type: Mapped[str] = mapped_column(String(20), nullable=False)  # PICKUP, RETURN
    odometer_reading_km: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_percentage: Mapped[int] = mapped_column(Integer, nullable=False)
    cleanliness_status: Mapped[str] = mapped_column(String(30), default="CLEAN", server_default="CLEAN", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    customer_signature_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    inspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "inspection_type IN ('PICKUP', 'RETURN')",
            name="chk_inspection_type",
        ),
        CheckConstraint(
            "fuel_percentage >= 0 AND fuel_percentage <= 100",
            name="chk_inspection_fuel_percentage",
        ),
        CheckConstraint(
            "odometer_reading_km >= 0",
            name="chk_inspection_odometer_positive",
        ),
    )

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="inspections")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="inspections")
    inspector: Mapped["User"] = relationship("User")
    damage_records: Mapped[List["InspectionDamageRecord"]] = relationship(
        "InspectionDamageRecord", back_populates="inspection", cascade="all, delete-orphan"
    )
    photos: Mapped[List["InspectionPhoto"]] = relationship(
        "InspectionPhoto", back_populates="inspection", cascade="all, delete-orphan"
    )


class InspectionDamageRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "inspection_damage_records"

    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    area: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    estimated_repair_cost_minor: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)

    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="damage_records")
    photos: Mapped[List["InspectionPhoto"]] = relationship("InspectionPhoto", back_populates="damage_record")


class InspectionPhoto(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "inspection_photos"

    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    damage_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspection_damage_records.id", ondelete="SET NULL"),
        nullable=True,
    )
    storage_key: Mapped[str] = mapped_column(String(300), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="photos")
    damage_record: Mapped[Optional["InspectionDamageRecord"]] = relationship("InspectionDamageRecord", back_populates="photos")
