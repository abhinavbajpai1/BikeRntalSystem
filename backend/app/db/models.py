# Aggregate all models so Base.metadata contains complete relational schema
from app.db.base import Base

# Module models
from app.modules.auth.models import Role, User, UserRole
from app.modules.partners.models import Partner, PartnerAgreement
from app.modules.fleet.models import City, Location, Vehicle, VehicleDocument
from app.modules.pricing.models import RentalPlan
from app.modules.bookings.models import Booking, BookingPriceSnapshot
from app.modules.payments.models import Payment, PaymentEvent, Refund, Deposit
from app.modules.inspections.models import Inspection, InspectionDamageRecord, InspectionPhoto
from app.modules.settlements.models import Settlement, SettlementItem, PayoutAttempt
from app.modules.audit.models import AuditLog

__all__ = [
    "Base",
    "Role",
    "User",
    "UserRole",
    "Partner",
    "PartnerAgreement",
    "City",
    "Location",
    "Vehicle",
    "VehicleDocument",
    "RentalPlan",
    "Booking",
    "BookingPriceSnapshot",
    "Payment",
    "PaymentEvent",
    "Refund",
    "Deposit",
    "Inspection",
    "InspectionDamageRecord",
    "InspectionPhoto",
    "Settlement",
    "SettlementItem",
    "PayoutAttempt",
    "AuditLog",
]
