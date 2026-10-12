import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Partner(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "partners"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tax_identifier: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        server_default="PENDING",
        nullable=False,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    bank_account_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "verification_status IN ('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED')",
            name="chk_partner_verification_status",
        ),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="partner_profile")
    agreements: Mapped[List["PartnerAgreement"]] = relationship("PartnerAgreement", back_populates="partner", cascade="all, delete-orphan")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="partner")
    settlements: Mapped[List["Settlement"]] = relationship("Settlement", back_populates="partner")


class PartnerAgreement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "partner_agreements"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agreement_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    commission_rate_basis_points: Mapped[int] = mapped_column(Integer, nullable=False)  # 2000 = 20.00%
    payout_cycle: Mapped[str] = mapped_column(String(30), default="WEEKLY", server_default="WEEKLY", nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    terms_document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "commission_rate_basis_points >= 0 AND commission_rate_basis_points <= 10000",
            name="chk_partner_commission_basis_points",
        ),
        CheckConstraint(
            "payout_cycle IN ('WEEKLY', 'BIWEEKLY', 'MONTHLY')",
            name="chk_partner_payout_cycle",
        ),
    )

    partner: Mapped["Partner"] = relationship("Partner", back_populates="agreements")
