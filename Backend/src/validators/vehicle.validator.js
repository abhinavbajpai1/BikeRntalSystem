
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
      .transform((value) => value.replace(/[\s-]/g, "").toUpperCase()),

    make: z.string().trim().min(1).max(100),

    model: z.string().trim().min(1).max(100),

    manufacturingYear: z
      .number()
      .int()
      .min(1980)
      .max(new Date().getFullYear() + 1, {
        message: "Year is too far in the future",
      }),

    fuelType: z.enum([
      "PETROL",
      "DIESEL",
      "ELECTRIC",
      "HYBRID",
      "CNG",
      "LPG",
    ]),

    transmission: z.enum(["MANUAL", "AUTOMATIC"]),

    seatingCapacity: z.number().int().min(1).max(100),
  })
  .strict()
  .superRefine((data, ctx) => {
    if (data.ownerType === "PARTNER" && !data.partnerId) {
      ctx.addIssue({
        code: "custom",
        path: ["partnerId"],
        message: "partnerId is required for PARTNER vehicles",
      });
    }

    if (data.ownerType === "COMPANY" && data.partnerId != null) {
      ctx.addIssue({
        code: "custom",
        path: ["partnerId"],
        message: "partnerId must be empty for COMPANY vehicles",
      });
    }
  });

const vehicleSchema = baseVehicleSchema;

const updateVehicleSchema = z
  .object({
    registrationNumber: baseVehicleSchema.shape.registrationNumber.optional(),

    make: baseVehicleSchema.shape.make.optional(),

    model: baseVehicleSchema.shape.model.optional(),

    manufacturingYear:
      baseVehicleSchema.shape.manufacturingYear.optional(),

    fuelType: baseVehicleSchema.shape.fuelType.optional(),

    transmission: baseVehicleSchema.shape.transmission.optional(),

    seatingCapacity: baseVehicleSchema.shape.seatingCapacity.optional(),
  })
  .strict()
  .refine((data) => Object.keys(data).length > 0, {
    message: "At least one field must be provided",
  });

module.exports = {
  vehicleSchema,
  baseVehicleSchema,
  updateVehicleSchema,
};
;
