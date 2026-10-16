const { z } = require("zod");

const baseVehicleSchema = z
  .object({
    ownerType: z.enum(["COMPANY", "PARTNER"]),
    partnerId: z.string().uuid().nullish(),
    registrationNumber: z
      .string()
      .trim()
      .min(1, "Registration number is required")
      .max(20)
      .transform((v) => v.replace(/[\s-]/g, "").toUpperCase()),
    make: z.string().trim().min(1).max(100),
    model: z.string().trim().min(1).max(100),
    manufacturingYear: z.number().int().min(1980),
    fuelType: z.enum(["PETROL", "DIESEL", "ELECTRIC", "HYBRID", "CNG", "LPG"]),
    transmission: z.enum(["MANUAL", "AUTOMATIC"]),
    seatingCapacity: z.number().int().min(1).max(100),
  })
  .strict();

const withRules = (schema) =>
  schema
    .refine(
      (d) =>
        d.manufacturingYear === undefined ||
        d.manufacturingYear <= new Date().getFullYear() + 1,
      { path: ["manufacturingYear"], message: "Year is too far in the future" },
    )
    .refine((d) => d.ownerType !== "PARTNER" || !!d.partnerId, {
      path: ["partnerId"],
      message: "partnerId is required for PARTNER vehicles",
    })
    .refine((d) => d.ownerType !== "COMPANY" || !d.partnerId, {
      path: ["partnerId"],
      message: "partnerId must be empty for COMPANY vehicles",
    });

const vehicleSchema = withRules(baseVehicleSchema);

module.exports = { vehicleSchema, baseVehicleSchema };
