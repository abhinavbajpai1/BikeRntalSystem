# Vroom Vroom

## Production-Oriented Vehicle Rental and Subscription Platform

Vroom Vroom is a modular vehicle rental and subscription platform designed to handle concurrent bookings, dual-fleet ownership (company-owned and partner-owned), isolated financial accounting (rentals, security deposits, refunds, and partner settlements), and end-to-end vehicle inspection workflows.

---

## 1. System Architecture

* **Frontend**: Next.js 15 (App Router), React 19, TypeScript (strict), Tailwind CSS, Lucide icons, Zod.
* **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 (typed async ORM), Alembic migrations, Pydantic v2.
* **Database**: PostgreSQL 17 with `btree_gist` extension for zero-overbooking range exclusion constraints (`tsrange`), UUID primary keys, and integer minor units (paise) for monetary integrity.
* **Architecture Style**: Modular Monolith with clean domain boundaries (`auth`, `users`, `partners`, `fleet`, `pricing`, `bookings`, `availability`, `payments`, `inspections`, `settlements`, `audit`, `notifications`).

---

## 2. Relational Schema & 22 Domain Entities

1. `roles` & `users` & `user_roles`: Multi-role RBAC authorization (`CUSTOMER`, `PARTNER`, `OPERATIONS`, `FLEET_MANAGER`, `ADMIN`).
2. `partners` & `partner_agreements`: Partner onboarding, tax identifiers, and versioned commission agreements.
3. `cities` & `locations`: Multi-hub physical stationing and expansion hierarchy.
4. `vehicles` & `vehicle_documents`: Strict ownership check constraints (`COMPANY` vs `PARTNER`), odometers, and fuel logs.
5. `rental_plans`: Fixed-duration and subscription tiers with daily/monthly mileage allowances and excess rates.
6. `bookings` & `booking_price_snapshots`: PostgreSQL `tsrange` exclusion constraints preventing overlapping bookings, and frozen historical commercial terms.
7. `payments`, `payment_events`, `refunds`, and `deposits`: Idempotency keys, mock payment state machine, and isolated escrow deposits.
8. `inspections`, `inspection_damage_records`, and `inspection_photos`: Pre-rental pickup and post-rental return condition audits.
9. `settlements`, `settlement_items`, and `payout_attempts`: Partner payout runs with historical commission calculation.
10. `audit_logs`: Tamper-resistant append-only operational event logging.

---

## 3. Quick Start & Local Development

### Prerequisites
* Python 3.12+
* Node.js v20+ / v22+ and npm
* PostgreSQL 17 or Docker

### Step 1: Environment Setup
```bash
cp .env.example .env
```
Ensure your PostgreSQL credentials in `.env` match your local setup:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/vroomvroom
DATABASE_URL_SYNC=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/vroomvroom
```

### Step 2: Database Migrations
Run the Alembic migration to create all 22 domain tables and enable `btree_gist`:
```bash
cd backend
alembic upgrade head
python scripts/seed_data.py
```

### Step 3: Run the Backend
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation: `http://127.0.0.1:8000/docs`

### Step 4: Run the Frontend
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000`

---

## 4. Running the Automated Test Suite

```bash
# Run backend test suite
python -m pytest backend/tests -v
```
Tests verify:
* API health and readiness probes with correlation IDs.
* FastAPI OpenAPI specification accessibility.
* Vehicle ownership invariants (company vs partner).
* Financial precision in integer minor units (paise).
* Security deposit isolation from rental revenues.
