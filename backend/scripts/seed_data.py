import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from passlib.context import CryptContext
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.modules.auth.models import Role, User, UserRole
from app.modules.partners.models import Partner, PartnerAgreement
from app.modules.fleet.models import City, Location, Vehicle
from app.modules.pricing.models import RentalPlan

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    async with AsyncSessionLocal() as session:
        print("🌱 Seeding Vroom Vroom initial data...")

        # 1. System Roles
        roles_data = [
            ("CUSTOMER", "Standard customer account for vehicle discovery and booking"),
            ("PARTNER", "Vehicle host offering vehicles for rental"),
            ("OPERATIONS", "Ground staff conducting vehicle pickup and return inspections"),
            ("FLEET_MANAGER", "Fleet manager reviewing vehicles and maintenance intervals"),
            ("ADMIN", "System administrator with full operational access"),
        ]
        created_roles = {}
        for name, desc in roles_data:
            stmt = select(Role).where(Role.name == name)
            res = await session.execute(stmt)
            role = res.scalar_one_or_none()
            if not role:
                role = Role(name=name, description=desc)
                session.add(role)
                await session.flush()
            created_roles[name] = role

        # 2. Launch City (Bangalore)
        stmt = select(City).where(City.code == "BLR")
        res = await session.execute(stmt)
        city = res.scalar_one_or_none()
        if not city:
            city = City(
                code="BLR",
                name="Bengaluru",
                state="Karnataka",
                country="India",
                is_active=True,
            )
            session.add(city)
            await session.flush()

        # 3. Locations / Pickup Hubs
        hubs_data = [
            ("Indiranagar Hub", "100ft Road, Indiranagar, Bengaluru, 560038", 12.9784, 77.6408),
            ("Koramangala Hub", "80ft Road, 4th Block, Koramangala, Bengaluru, 560034", 12.9352, 77.6245),
            ("Kempegowda Airport Hub", "KIA Terminal 1 Transportation Area, Devanahalli, Bengaluru, 560300", 13.1986, 77.7066),
        ]
        created_locations = []
        for name, address, lat, lon in hubs_data:
            stmt = select(Location).where(Location.name == name)
            res = await session.execute(stmt)
            loc = res.scalar_one_or_none()
            if not loc:
                loc = Location(
                    city_id=city.id,
                    name=name,
                    address=address,
                    latitude=lat,
                    longitude=lon,
                    is_active=True,
                )
                session.add(loc)
                await session.flush()
            created_locations.append(loc)

        # 4. Rental & Subscription Plans
        plans_data = [
            (
                "Standard Daily - Economy",
                "DAILY_ECONOMY",
                "FIXED_DURATION",
                "ECONOMY",
                24,
                720,
                150000,    # ₹1,500/day
                "DAY",
                200,       # 200 km/day
                1200,      # ₹12/km excess
                300000,    # ₹3,000 deposit
                1800,      # 18.00% GST
            ),
            (
                "Standard Daily - Premium SUV",
                "DAILY_SUV",
                "FIXED_DURATION",
                "PREMIUM",
                24,
                720,
                350000,    # ₹3,500/day
                "DAY",
                250,       # 250 km/day
                1500,      # ₹15/km excess
                700000,    # ₹7,000 deposit
                1800,      # 18.00% GST
            ),
            (
                "Monthly Flex Subscription",
                "MONTHLY_FLEX",
                "SUBSCRIPTION",
                "COMFORT",
                720,
                8760,
                3200000,   # ₹32,000/month
                "MONTH",
                2500,      # 2,500 km/month
                1000,      # ₹10/km excess
                1000000,   # ₹10,000 deposit
                1800,      # 18.00% GST
            ),
        ]
        for name, code, rtype, tier, min_h, max_h, rate, unit, km, ex_km, dep, tax in plans_data:
            stmt = select(RentalPlan).where(RentalPlan.code == code)
            res = await session.execute(stmt)
            plan = res.scalar_one_or_none()
            if not plan:
                plan = RentalPlan(
                    city_id=city.id,
                    name=name,
                    code=code,
                    rental_type=rtype,
                    tier=tier,
                    min_duration_hours=min_h,
                    max_duration_hours=max_h,
                    base_rate_minor=rate,
                    rate_unit=unit,
                    mileage_allowance_km_per_day=km,
                    excess_mileage_rate_minor=ex_km,
                    security_deposit_minor=dep,
                    tax_rate_basis_points=tax,
                    is_active=True,
                )
                session.add(plan)

        # 5. Admin & Partner Users
        stmt = select(User).where(User.email == "admin@vroomvroom.com")
        res = await session.execute(stmt)
        admin_user = res.scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                email="admin@vroomvroom.com",
                password_hash=pwd_context.hash("Admin@Vroom2026"),
                full_name="Fleet Operations Admin",
                phone="+919876543210",
                status="ACTIVE",
                is_verified=True,
            )
            session.add(admin_user)
            await session.flush()
            session.add(UserRole(user_id=admin_user.id, role_id=created_roles["ADMIN"].id))
            session.add(UserRole(user_id=admin_user.id, role_id=created_roles["OPERATIONS"].id))

        stmt = select(User).where(User.email == "partner@zenithfleet.com")
        res = await session.execute(stmt)
        partner_user = res.scalar_one_or_none()
        if not partner_user:
            partner_user = User(
                email="partner@zenithfleet.com",
                password_hash=pwd_context.hash("Partner@Zenith2026"),
                full_name="Zenith Fleet Host",
                phone="+919876543211",
                status="ACTIVE",
                is_verified=True,
            )
            session.add(partner_user)
            await session.flush()
            session.add(UserRole(user_id=partner_user.id, role_id=created_roles["PARTNER"].id))

            partner_profile = Partner(
                user_id=partner_user.id,
                business_name="Zenith Urban Fleets Pvt Ltd",
                tax_identifier="29AAACZ1234F1Z5",
                verification_status="APPROVED",
                approved_at=datetime.now(timezone.utc),
                approved_by_id=admin_user.id,
            )
            session.add(partner_profile)
            await session.flush()

            agreement = PartnerAgreement(
                partner_id=partner_profile.id,
                agreement_code="AGR-ZENITH-2026-01",
                commission_rate_basis_points=2000,  # 20.00%
                payout_cycle="WEEKLY",
                valid_from=datetime.now(timezone.utc),
                is_active=True,
            )
            session.add(agreement)

        await session.commit()
        print("✅ Database successfully seeded with roles, locations, plans, admin, and partner profiles!")


if __name__ == "__main__":
    asyncio.run(seed())
