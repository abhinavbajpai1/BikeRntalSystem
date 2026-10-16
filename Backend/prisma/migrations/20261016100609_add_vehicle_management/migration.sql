-- CreateEnum
CREATE TYPE "VehicleOwnerType" AS ENUM ('COMPANY', 'PARTNER');

-- CreateEnum
CREATE TYPE "VehicleStatus" AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'ACTIVE', 'MAINTENANCE', 'RETIRED');

-- CreateEnum
CREATE TYPE "VehicleFuelType" AS ENUM ('PETROL', 'DIESEL', 'ELECTRIC', 'HYBRID', 'CNG', 'LPG');

-- CreateEnum
CREATE TYPE "VehicleTransmission" AS ENUM ('MANUAL', 'AUTOMATIC');

-- CreateTable
CREATE TABLE "user_sessions" (
    "sid" VARCHAR NOT NULL,
    "sess" JSON NOT NULL,
    "expire" TIMESTAMP(6) NOT NULL,

    CONSTRAINT "user_sessions_pkey" PRIMARY KEY ("sid")
);

-- CreateTable
CREATE TABLE "vehicles" (
    "id" UUID NOT NULL,
    "owner_type" "VehicleOwnerType" NOT NULL,
    "partner_id" UUID,
    "registration_number" VARCHAR(20) NOT NULL,
    "make" VARCHAR(100) NOT NULL,
    "model" VARCHAR(100) NOT NULL,
    "manufacturing_year" INTEGER NOT NULL,
    "fuel_type" "VehicleFuelType" NOT NULL,
    "transmission" "VehicleTransmission" NOT NULL,
    "seating_capacity" INTEGER NOT NULL,
    "status" "VehicleStatus" NOT NULL DEFAULT 'DRAFT',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "vehicles_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "IDX_user_sessions_expire" ON "user_sessions"("expire");

-- CreateIndex
CREATE UNIQUE INDEX "vehicles_registration_number_key" ON "vehicles"("registration_number");

-- CreateIndex
CREATE INDEX "vehicles_owner_type_idx" ON "vehicles"("owner_type");

-- CreateIndex
CREATE INDEX "vehicles_partner_id_idx" ON "vehicles"("partner_id");

-- CreateIndex
CREATE INDEX "vehicles_status_idx" ON "vehicles"("status");

-- CreateIndex
CREATE INDEX "vehicles_make_model_idx" ON "vehicles"("make", "model");

-- AddForeignKey
ALTER TABLE "vehicles" ADD CONSTRAINT "vehicles_partner_id_fkey" FOREIGN KEY ("partner_id") REFERENCES "partners"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
