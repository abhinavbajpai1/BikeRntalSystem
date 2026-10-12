"""Initial schema with 22 core domain tables and btree_gist extension

Revision ID: 20261012_000000
Revises: 
Create Date: 2026-10-12 05:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20261012_000000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Ensure btree_gist extension for PostgreSQL range exclusion constraints
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # 1. roles
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_roles_name", "roles", ["name"])

    # 2. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("status", sa.String(30), server_default="ACTIVE", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('ACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION')", name="chk_user_status"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_phone", "users", ["phone"])

    # 3. user_roles
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])

    # 4. partners
    op.create_table(
        "partners",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("business_name", sa.String(200), nullable=False),
        sa.Column("tax_identifier", sa.String(50), unique=True, nullable=False),
        sa.Column("verification_status", sa.String(30), server_default="PENDING", nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bank_account_details", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("verification_status IN ('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED')", name="chk_partner_verification_status"),
    )
    op.create_index("ix_partners_tax_identifier", "partners", ["tax_identifier"])

    # 5. partner_agreements
    op.create_table(
        "partner_agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agreement_code", sa.String(50), unique=True, nullable=False),
        sa.Column("commission_rate_basis_points", sa.Integer(), nullable=False),
        sa.Column("payout_cycle", sa.String(30), server_default="WEEKLY", nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("terms_document_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("commission_rate_basis_points >= 0 AND commission_rate_basis_points <= 10000", name="chk_partner_commission_basis_points"),
        sa.CheckConstraint("payout_cycle IN ('WEEKLY', 'BIWEEKLY', 'MONTHLY')", name="chk_partner_payout_cycle"),
    )

    # 6. cities
    op.create_table(
        "cities",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("code", sa.String(10), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), server_default="India", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cities_code", "cities", ["code"])

    # 7. locations
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("city_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("address", sa.String(300), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_locations_city_id", "locations", ["city_id"])

    # 8. vehicles
    op.create_table(
        "vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("ownership_type", sa.String(20), nullable=False),
        sa.Column("vin", sa.String(50), unique=True, nullable=False),
        sa.Column("registration_number", sa.String(30), unique=True, nullable=False),
        sa.Column("make", sa.String(50), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("body_type", sa.String(30), nullable=False),
        sa.Column("transmission", sa.String(20), nullable=False),
        sa.Column("fuel_type", sa.String(20), nullable=False),
        sa.Column("seating_capacity", sa.Integer(), server_default="5", nullable=False),
        sa.Column("status", sa.String(30), server_default="ACTIVE", nullable=False),
        sa.Column("current_odometer_km", sa.Integer(), server_default="0", nullable=False),
        sa.Column("current_fuel_percentage", sa.Integer(), server_default="100", nullable=False),
        sa.Column("primary_image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("ownership_type IN ('COMPANY', 'PARTNER')", name="chk_vehicle_ownership_type"),
        sa.CheckConstraint(
            "(ownership_type = 'COMPANY' AND partner_id IS NULL) OR (ownership_type = 'PARTNER' AND partner_id IS NOT NULL)",
            name="chk_vehicle_ownership_partner_consistency",
        ),
        sa.CheckConstraint("status IN ('ACTIVE', 'MAINTENANCE', 'RETIRED', 'PENDING_APPROVAL')", name="chk_vehicle_status"),
        sa.CheckConstraint("current_fuel_percentage >= 0 AND current_fuel_percentage <= 100", name="chk_vehicle_fuel_percentage"),
        sa.CheckConstraint("current_odometer_km >= 0", name="chk_vehicle_odometer_non_negative"),
    )
    op.create_index("ix_vehicles_vin", "vehicles", ["vin"])
    op.create_index("ix_vehicles_registration_number", "vehicles", ["registration_number"])
    op.create_index("ix_vehicles_make", "vehicles", ["make"])
    op.create_index("ix_vehicles_model", "vehicles", ["model"])
    op.create_index("ix_vehicles_status", "vehicles", ["status"])

    # 9. vehicle_documents
    op.create_table(
        "vehicle_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("storage_key", sa.String(300), nullable=False),
        sa.Column("document_url", sa.String(500), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "document_type IN ('REGISTRATION_CERTIFICATE', 'INSURANCE_POLICY', 'POLLUTION_UNDER_CONTROL', 'FITNESS_CERTIFICATE')",
            name="chk_vehicle_document_type",
        ),
    )

    # 10. rental_plans
    op.create_table(
        "rental_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("city_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("rental_type", sa.String(30), nullable=False),
        sa.Column("tier", sa.String(30), nullable=False),
        sa.Column("min_duration_hours", sa.Integer(), server_default="24", nullable=False),
        sa.Column("max_duration_hours", sa.Integer(), server_default="720", nullable=False),
        sa.Column("base_rate_minor", sa.BigInteger(), nullable=False),
        sa.Column("rate_unit", sa.String(20), server_default="DAY", nullable=False),
        sa.Column("mileage_allowance_km_per_day", sa.Integer(), server_default="200", nullable=False),
        sa.Column("excess_mileage_rate_minor", sa.BigInteger(), server_default="1200", nullable=False),
        sa.Column("security_deposit_minor", sa.BigInteger(), server_default="300000", nullable=False),
        sa.Column("tax_rate_basis_points", sa.Integer(), server_default="1800", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rental_type IN ('FIXED_DURATION', 'SUBSCRIPTION')", name="chk_rental_plan_type"),
        sa.CheckConstraint("tier IN ('ECONOMY', 'COMFORT', 'PREMIUM')", name="chk_rental_plan_tier"),
        sa.CheckConstraint("rate_unit IN ('HOUR', 'DAY', 'MONTH')", name="chk_rental_plan_rate_unit"),
        sa.CheckConstraint("base_rate_minor >= 0 AND security_deposit_minor >= 0 AND excess_mileage_rate_minor >= 0", name="chk_rental_plan_monetary_positive"),
        sa.CheckConstraint("min_duration_hours > 0 AND max_duration_hours >= min_duration_hours", name="chk_rental_plan_durations"),
    )
    op.create_index("ix_rental_plans_code", "rental_plans", ["code"])

    # 11. bookings (with PostgreSQL Range Exclusion Constraint)
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("booking_reference", sa.String(40), unique=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rental_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rental_plans.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rental_type", sa.String(30), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("booking_period", postgresql.TSTZRANGE(), nullable=False),
        sa.Column("status", sa.String(30), server_default="HELD", nullable=False),
        sa.Column("hold_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_pickup_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_return_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.String(300), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("end_time > start_time", name="chk_booking_period_valid"),
        sa.CheckConstraint("status IN ('DRAFT', 'HELD', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'EXPIRED')", name="chk_booking_status"),
    )
    op.create_index("ix_bookings_booking_reference", "bookings", ["booking_reference"])
    op.create_index("ix_bookings_status", "bookings", ["status"])

    # Concurrency safe exclusion constraint: Zero overlapping active/held bookings per vehicle
    op.execute("""
        ALTER TABLE bookings ADD CONSTRAINT no_overlapping_active_vehicle_bookings
        EXCLUDE USING gist (
            vehicle_id WITH =,
            booking_period WITH &&
        ) WHERE (status IN ('HELD', 'CONFIRMED', 'ACTIVE'));
    """)

    # 12. booking_price_snapshots
    op.create_table(
        "booking_price_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("currency", sa.String(10), server_default="INR", nullable=False),
        sa.Column("base_rate_minor", sa.BigInteger(), nullable=False),
        sa.Column("duration_units", sa.Integer(), nullable=False),
        sa.Column("unit_type", sa.String(20), nullable=False),
        sa.Column("base_rental_amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("mileage_allowance_km", sa.Integer(), nullable=False),
        sa.Column("excess_mileage_rate_minor", sa.BigInteger(), nullable=False),
        sa.Column("security_deposit_minor", sa.BigInteger(), nullable=False),
        sa.Column("tax_rate_basis_points", sa.Integer(), nullable=False),
        sa.Column("tax_amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("discount_amount_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("total_payable_minor", sa.BigInteger(), nullable=False),
        sa.Column("snapshot_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "base_rental_amount_minor >= 0 AND tax_amount_minor >= 0 AND security_deposit_minor >= 0 AND total_payable_minor >= 0",
            name="chk_price_snapshot_non_negative",
        ),
    )

    # 13. payments
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("idempotency_key", sa.String(100), unique=True, nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(10), server_default="INR", nullable=False),
        sa.Column("payment_type", sa.String(30), server_default="RENTAL_FEE", nullable=False),
        sa.Column("status", sa.String(30), server_default="PENDING", nullable=False),
        sa.Column("provider", sa.String(50), server_default="MOCK_PROVIDER", nullable=False),
        sa.Column("provider_reference", sa.String(100), nullable=True),
        sa.Column("failure_reason", sa.String(255), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount_minor > 0", name="chk_payment_amount_positive"),
        sa.CheckConstraint("status IN ('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'REFUNDED')", name="chk_payment_status"),
        sa.CheckConstraint("payment_type IN ('RENTAL_FEE', 'SECURITY_DEPOSIT', 'EXCESS_MILEAGE', 'DAMAGE_FEE')", name="chk_payment_type"),
    )
    op.create_index("ix_payments_idempotency_key", "payments", ["idempotency_key"])
    op.create_index("ix_payments_status", "payments", ["status"])

    # 14. payment_events
    op.create_table(
        "payment_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 15. refunds
    op.create_table(
        "refunds",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), server_default="PENDING", nullable=False),
        sa.Column("provider_refund_reference", sa.String(100), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount_minor > 0", name="chk_refund_amount_positive"),
        sa.CheckConstraint("status IN ('PENDING', 'SUCCEEDED', 'FAILED')", name="chk_refund_status"),
    )

    # 16. deposits
    op.create_table(
        "deposits",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), unique=True, nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(30), server_default="PENDING_COLLECTION", nullable=False),
        sa.Column("deducted_amount_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("refunded_amount_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("deduction_reason", sa.String(300), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount_minor >= 0 AND deducted_amount_minor >= 0 AND refunded_amount_minor >= 0", name="chk_deposit_amounts_positive"),
        sa.CheckConstraint("status IN ('PENDING_COLLECTION', 'HELD', 'REFUNDED_FULL', 'REFUNDED_PARTIAL', 'DEDUCTED')", name="chk_deposit_status"),
    )

    # 17. inspections
    op.create_table(
        "inspections",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("inspector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("inspection_type", sa.String(20), nullable=False),
        sa.Column("odometer_reading_km", sa.Integer(), nullable=False),
        sa.Column("fuel_percentage", sa.Integer(), nullable=False),
        sa.Column("cleanliness_status", sa.String(30), server_default="CLEAN", nullable=False),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("customer_signature_confirmed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("inspection_type IN ('PICKUP', 'RETURN')", name="chk_inspection_type"),
        sa.CheckConstraint("fuel_percentage >= 0 AND fuel_percentage <= 100", name="chk_inspection_fuel_percentage"),
        sa.CheckConstraint("odometer_reading_km >= 0", name="chk_inspection_odometer_positive"),
    )

    # 18. inspection_damage_records
    op.create_table(
        "inspection_damage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("area", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(30), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("estimated_repair_cost_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 19. inspection_photos
    op.create_table(
        "inspection_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("damage_record_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspection_damage_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("storage_key", sa.String(300), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("caption", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 20. settlements
    op.create_table(
        "settlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("settlement_reference", sa.String(50), unique=True, nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gross_rental_amount_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("commission_deducted_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("adjustments_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("net_payable_minor", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("status", sa.String(30), server_default="DRAFT", nullable=False),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('DRAFT', 'APPROVED', 'PROCESSED', 'FAILED')", name="chk_settlement_status"),
        sa.CheckConstraint("period_end >= period_start", name="chk_settlement_period_valid"),
    )
    op.create_index("ix_settlements_settlement_reference", "settlements", ["settlement_reference"])

    # 21. settlement_items
    op.create_table(
        "settlement_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("settlement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("settlements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), unique=True, nullable=False),
        sa.Column("gross_amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("commission_rate_basis_points", sa.Integer(), nullable=False),
        sa.Column("commission_amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("net_partner_share_minor", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("commission_rate_basis_points >= 0 AND commission_rate_basis_points <= 10000", name="chk_item_commission_basis_points"),
        sa.CheckConstraint("gross_amount_minor >= 0 AND commission_amount_minor >= 0 AND net_partner_share_minor >= 0", name="chk_item_amounts_non_negative"),
    )

    # 22. payout_attempts
    op.create_table(
        "payout_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("settlement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("settlements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attempt_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(30), server_default="INITIATED", nullable=False),
        sa.Column("reference", sa.String(100), nullable=True),
        sa.Column("error_message", sa.String(300), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount_minor > 0", name="chk_payout_amount_positive"),
        sa.CheckConstraint("status IN ('INITIATED', 'SUCCEEDED', 'FAILED')", name="chk_payout_status"),
    )

    # 23. audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("changes", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("payout_attempts")
    op.drop_table("settlement_items")
    op.drop_table("settlements")
    op.drop_table("inspection_photos")
    op.drop_table("inspection_damage_records")
    op.drop_table("inspections")
    op.drop_table("deposits")
    op.drop_table("refunds")
    op.drop_table("payment_events")
    op.drop_table("payments")
    op.drop_table("booking_price_snapshots")
    op.drop_table("bookings")
    op.drop_table("rental_plans")
    op.drop_table("vehicle_documents")
    op.drop_table("vehicles")
    op.drop_table("locations")
    op.drop_table("cities")
    op.drop_table("partner_agreements")
    op.drop_table("partners")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
