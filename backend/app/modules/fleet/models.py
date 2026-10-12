import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class City(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cities"

    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="India", server_default="India", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    # Relationships
    locations: Mapped[List["Location"]] = relationship("Location", back_populates="city", cascade="all, delete-orphan")


class Location(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "locations"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="locations")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="location")


class Vehicle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "vehicles"

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    ownership_type: Mapped[str] = mapped_column(String(20), nullable=False)  # COMPANY or PARTNER
    vin: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    registration_number: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    body_type: Mapped[str] = mapped_column(String(30), nullable=False)  # HATCHBACK, SEDAN, SUV
    transmission: Mapped[str] = mapped_column(String(20), nullable=False)  # MANUAL, AUTOMATIC
    fuel_type: Mapped[str] = mapped_column(String(20), nullable=False)  # PETROL, DIESEL, ELECTRIC, HYBRID
    seating_capacity: Mapped[int] = mapped_column(Integer, default=5, server_default="5", nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
        server_default="ACTIVE",
        nullable=False,
        index=True,
    )
    current_odometer_km: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    current_fuel_percentage: Mapped[int] = mapped_column(Integer, default=100, server_default="100", nullable=False)
    primary_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "ownership_type IN ('COMPANY', 'PARTNER')",
            name="chk_vehicle_ownership_type",
        ),
        CheckConstraint(
            "(ownership_type = 'COMPANY' AND partner_id IS NULL) OR (ownership_type = 'PARTNER' AND partner_id IS NOT NULL)",
            name="chk_vehicle_ownership_partner_consistency",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'MAINTENANCE', 'RETIRED', 'PENDING_APPROVAL')",
            name="chk_vehicle_status",
        ),
        CheckConstraint(
            "current_fuel_percentage >= 0 AND current_fuel_percentage <= 100",
            name="chk_vehicle_fuel_percentage",
        ),
        CheckConstraint(
            "current_odometer_km >= 0",
            name="chk_vehicle_odometer_non_negative",
        ),
    )

    # Relationships
    location: Mapped["Location"] = relationship("Location", back_populates="vehicles")
    partner: Mapped[Optional["Partner"]] = relationship("Partner", back_populates="vehicles")
    documents: Mapped[List["VehicleDocument"]] = relationship("VehicleDocument", back_populates="vehicle", cascade="all, delete-orphan")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="vehicle")
    inspections: Mapped[List["Inspection"]] = relationship("Inspection", back_populates="vehicle")


class VehicleDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "vehicle_documents"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(300), nullable=False)
    document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('REGISTRATION_CERTIFICATE', 'INSURANCE_POLICY', 'POLLUTION_UNDER_CONTROL', 'FITNESS_CERTIFICATE')",
            name="chk_vehicle_document_type",
        ),
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="documents")
