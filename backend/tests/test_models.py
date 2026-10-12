import uuid
from datetime import datetime, timezone, timedelta
import pytest
from app.modules.auth.models import Role, User, UserRole
from app.modules.partners.models import Partner, PartnerAgreement
from app.modules.fleet.models import City, Location, Vehicle, VehicleDocument
from app.modules.pricing.models import RentalPlan
from app.modules.bookings.models import Booking, BookingPriceSnapshot
from app.modules.payments.models import Payment, Deposit, Refund
from app.modules.inspections.models import Inspection, InspectionDamageRecord
from app.modules.settlements.models import Settlement, SettlementItem
from app.modules.audit.models import AuditLog


def test_user_and_role_instantiation():
    user = User(
        email="customer@vroomvroom.com",
        password_hash="hashed_pw_argon2",
        full_name="Abhinav Test",
        status="ACTIVE",
    )
    role = Role(name="CUSTOMER", description="Vehicle renter")
    assert user.email == "customer@vroomvroom.com"
    assert user.status == "ACTIVE"
    assert role.name == "CUSTOMER"


def test_vehicle_ownership_invariants():
    city_id = uuid.uuid4()
    loc_id = uuid.uuid4()
    partner_id = uuid.uuid4()

    # Company-owned vehicle (partner_id must be None)
    company_car = Vehicle(
        location_id=loc_id,
        partner_id=None,
        ownership_type="COMPANY",
        vin="1HGCR2F83HA000001",
        registration_number="KA01AB1001",
        make="Hyundai",
        model="Creta",
        year=2024,
        body_type="SUV",
        transmission="AUTOMATIC",
        fuel_type="PETROL",
        status="ACTIVE",
        current_odometer_km=15200,
        current_fuel_percentage=95,
    )
    assert company_car.ownership_type == "COMPANY"
    assert company_car.partner_id is None

    # Partner-owned vehicle (partner_id must be present)
    partner_car = Vehicle(
        location_id=loc_id,
        partner_id=partner_id,
        ownership_type="PARTNER",
        vin="1HGCR2F83HA000002",
        registration_number="KA01CD2002",
        make="Tata",
        model="Nexon",
        year=2023,
        body_type="SUV",
        transmission="MANUAL",
        fuel_type="DIESEL",
        status="ACTIVE",
        current_odometer_km=28000,
        current_fuel_percentage=80,
    )
    assert partner_car.ownership_type == "PARTNER"
    assert partner_car.partner_id == partner_id


def test_pricing_and_booking_snapshot_monetary_precision():
    now = datetime.now(timezone.utc)
    booking_id = uuid.uuid4()

    # Pricing snapshot in integer minor units (paise: ₹1 = 100 paise)
    snapshot = BookingPriceSnapshot(
        booking_id=booking_id,
        currency="INR",
        base_rate_minor=250000,          # ₹2,500/day
        duration_units=3,                 # 3 days
        unit_type="DAY",
        base_rental_amount_minor=750000,  # ₹7,500
        mileage_allowance_km=600,         # 200 km/day * 3 days
        excess_mileage_rate_minor=1200,   # ₹12/km
        security_deposit_minor=300000,    # ₹3,000
        tax_rate_basis_points=1800,       # 18.00% GST
        tax_amount_minor=135000,          # 18% of 750000 = ₹1,350
        discount_amount_minor=0,
        total_payable_minor=1185000,      # ₹7,500 + ₹1,350 + ₹3,000 = ₹11,850
    )

    assert snapshot.base_rental_amount_minor == 750000
    assert snapshot.total_payable_minor == (
        snapshot.base_rental_amount_minor + snapshot.tax_amount_minor + snapshot.security_deposit_minor
    )
    # Ensure money is pure integer and not float
    assert isinstance(snapshot.total_payable_minor, int)


def test_deposit_and_settlement_isolation():
    booking_id = uuid.uuid4()
    deposit = Deposit(
        booking_id=booking_id,
        amount_minor=300000,  # ₹3,000
        status="HELD",
        deducted_amount_minor=0,
        refunded_amount_minor=0,
    )
    assert deposit.status == "HELD"
    assert deposit.deducted_amount_minor == 0
    assert deposit.refunded_amount_minor == 0

    settlement_id = uuid.uuid4()
    item = SettlementItem(
        settlement_id=settlement_id,
        booking_id=booking_id,
        gross_amount_minor=750000,          # ₹7,500
        commission_rate_basis_points=2000,  # 20.00%
        commission_amount_minor=150000,     # ₹1,500
        net_partner_share_minor=600000,     # ₹6,000
    )
    assert item.commission_amount_minor == 150000
    assert item.net_partner_share_minor == 600000
    assert item.gross_amount_minor - item.commission_amount_minor == item.net_partner_share_minor
