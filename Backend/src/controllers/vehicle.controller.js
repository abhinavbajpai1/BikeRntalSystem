const prisma = require("../lib/prisma");
const { vehicleSchema } = require("../validators/vehicle.validator");

async function createVehicle(req, res) {
  try {
    // 1. Validate the incoming request body.
    const validation = vehicleSchema.safeParse(req.body);

    
if (!validation.success) {
  return res.status(400).json({
    success: false,
    message: "Invalid vehicle data",
    errors: validation.error.issues.map((issue) => ({
      field: issue.path.join("."),
      message: issue.message,
    })),
  });
}

const data = validation.data;

// 2. Enforce vehicle ownership rules.
if (data.ownerType === "COMPANY" && data.partnerId) {
  return res.status(400).json({
    success: false,
    message: "Company-owned vehicles cannot have a partnerId",
  });
}

if (data.ownerType === "PARTNER" && !data.partnerId) {
  return res.status(400).json({
    success: false,
    message: "Partner-owned vehicles require a partnerId",
  });
}

// 3. Verify that the partner exists and is eligible.
if (data.ownerType === "PARTNER") {
  const partner = await prisma.partner.findUnique({
    where: { id: data.partnerId },
    select: {
      id: true,
      status: true,
    },
  });

  if (!partner) {
    return res.status(404).json({
      success: false,
      message: "Partner not found",
    });
  }

  if (partner.status !== "VERIFIED") {
    return res.status(409).json({
      success: false,
      message: "Vehicles can only be registered for verified partners",
    });
  }
}

// 4. Create the vehicle in PostgreSQL.
const vehicle = await prisma.vehicle.create({
  data: {
    ownerType: data.ownerType,
    partnerId: data.ownerType === "PARTNER" ? data.partnerId : null,
    registrationNumber: data.registrationNumber,
    make: data.make,
    model: data.model,
    manufacturingYear: data.manufacturingYear,
    fuelType: data.fuelType,
    transmission: data.transmission,
    seatingCapacity: data.seatingCapacity,
    status: "DRAFT",
  },
});

return res.status(201).json({
  success: true,
  message: "Vehicle created successfully",
  data: vehicle,
});
;
  } catch (error) {
    if (error.code === "P2002") {
      return res.status(409).json({
        success: false,
        message: "A vehicle with this registration number already exists",
      });
    }

    
if (error.code === "P2003") {
  return res.status(400).json({
    success: false,
    message: "Invalid partner reference",
  });
}

console.error("Create vehicle error:", error);

return res.status(500).json({
  success: false,
  message: "Unable to create vehicle",
});
;
  }
}

module.exports = { createVehicle };
