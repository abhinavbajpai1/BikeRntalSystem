const prisma = require("../lib/prisma");
const { vehicleSchema,updateVehicleSchema } = require("../validators/vehicle.validator");

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

// Keep these in sync with your Prisma enums.
const ALLOWED_FUEL_TYPES = new Set([
  "PETROL",
  "DIESEL",
  "ELECTRIC",
  "HYBRID",
  "CNG",
  "LPG",
]);
const ALLOWED_TRANSMISSIONS = new Set(["MANUAL", "AUTOMATIC"]);

const MAX_PAGE = 10000;
const MAX_LIMIT = 100;
const MAX_MAKE_LENGTH = 50;

function badRequest(res, message) {
  return res.status(400).json({ success: false, message });
}

async function listVehicles(req, res) {
  try {
    const { query } = req;

    // Pagination
    const page = Number(query.page ?? 1);
    const limit = Number(query.limit ?? 10);

    if (!Number.isInteger(page) || page < 1 || page > MAX_PAGE) {
      return badRequest(res, `page must be an integer between 1 and ${MAX_PAGE}`);
    }
    if (!Number.isInteger(limit) || limit < 1 || limit > MAX_LIMIT) {
      return badRequest(res, `limit must be an integer between 1 and ${MAX_LIMIT}`);
    }

    // Filters
    const where = { status: "ACTIVE" };

    if (query.make !== undefined) {
      if (typeof query.make !== "string") {
        return badRequest(res, "make must be a string");
      }
      const make = query.make.trim();
      if (make.length === 0 || make.length > MAX_MAKE_LENGTH) {
        return badRequest(
          res,
          `make must be between 1 and ${MAX_MAKE_LENGTH} characters`
        );
      }
      where.make = { contains: make, mode: "insensitive" };
    }

    if (query.fuelType !== undefined) {
      if (typeof query.fuelType !== "string" || !ALLOWED_FUEL_TYPES.has(query.fuelType)) {
        return badRequest(res, "Invalid fuelType");
      }
      where.fuelType = query.fuelType;
    }

    if (query.transmission !== undefined) {
      if (
        typeof query.transmission !== "string" ||
        !ALLOWED_TRANSMISSIONS.has(query.transmission)
      ) {
        return badRequest(res, "Invalid transmission");
      }
      where.transmission = query.transmission;
    }

    if (query.seatingCapacity !== undefined) {
      const seatingCapacity = Number(query.seatingCapacity);
      if (
        !Number.isInteger(seatingCapacity) ||
        seatingCapacity < 1 ||
        seatingCapacity > 100
      ) {
        return badRequest(res, "seatingCapacity must be an integer between 1 and 100");
      }
      where.seatingCapacity = seatingCapacity;
    }

    // Query PostgreSQL through Prisma
    const [vehicles, total] = await prisma.$transaction([
      prisma.vehicle.findMany({
        where,
        orderBy: [{ make: "asc" }, { model: "asc" }, { id: "asc" }],
        skip: (page - 1) * limit,
        take: limit,
        // registrationNumber and ownerType are intentionally left out of this
        // public listing. Add them back only for authenticated owners/admins.
        select: {
          id: true,
          make: true,
          model: true,
          manufacturingYear: true,
          fuelType: true,
          transmission: true,
          seatingCapacity: true,
          status: true,
          createdAt: true,
        },
      }),
      prisma.vehicle.count({ where }),
    ]);

    return res.status(200).json({
      success: true,
      data: vehicles,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error("List vehicles error:", error);

    return res.status(500).json({
      success: false,
      message: "Unable to retrieve vehicles",
    });
  }
}
async function getVehicleById(req, res) {
  try {
    const { id } = req.params;

    
// Validate the vehicle UUID.
if (
  typeof id !== "string" ||
  !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)
) {
  return res.status(400).json({
    success: false,
    message: "Invalid vehicle ID",
  });
}

// Retrieve only active vehicles.
const vehicle = await prisma.vehicle.findFirst({
  where: {
    id,
    status: "ACTIVE",
  },
  select: {
    id: true,
    ownerType: true,
    registrationNumber: true,
    make: true,
    model: true,
    manufacturingYear: true,
    fuelType: true,
    transmission: true,
    seatingCapacity: true,
    status: true,
    createdAt: true,
  },
});

if (!vehicle) {
  return res.status(404).json({
    success: false,
    message: "Vehicle not found",
  });
}

return res.status(200).json({
  success: true,
  data: vehicle,
});
;
  } catch (error) {
    console.error("Get vehicle by ID error:", error);

    
return res.status(500).json({
  success: false,
  message: "Unable to retrieve vehicle",
});;
  }
}

async function listAllVehicles(req, res) {
  try {
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 10);

    if (
      !Number.isInteger(page) ||
      page < 1 ||
      !Number.isInteger(limit) ||
      limit < 1 ||
      limit > 100
    ) {
      return res.status(400).json({
        success: false,
        message: "Invalid pagination parameters",
      });
    }

    const { status, ownerType, make, fuelType } = req.query;

    const validStatuses = [
      "DRAFT",
      "PENDING_APPROVAL",
      "ACTIVE",
      "MAINTENANCE",
      "RETIRED",
    ];

    const validOwnerTypes = ["COMPANY", "PARTNER"];

    const validFuelTypes = [
      "PETROL",
      "DIESEL",
      "ELECTRIC",
      "HYBRID",
      "CNG",
      "LPG",
    ];

    if (status && !validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        message: "Invalid vehicle status",
      });
    }

    if (ownerType && !validOwnerTypes.includes(ownerType)) {
      return res.status(400).json({
        success: false,
        message: "Invalid vehicle owner type",
      });
    }

    if (fuelType && !validFuelTypes.includes(fuelType)) {
      return res.status(400).json({
        success: false,
        message: "Invalid fuel type",
      });
    }

    if (make !== undefined && make.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: "Make cannot be empty",
      });
    }

    const where = {
      ...(status && { status }),
      ...(ownerType && { ownerType }),
      ...(fuelType && { fuelType }),
      ...(make && {
        make: {
          contains: make.trim(),
          mode: "insensitive",
        },
      }),
    };

    const [vehicles, total] = await prisma.$transaction([
      prisma.vehicle.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: [
          { createdAt: "desc" },
          { id: "asc" },
        ],
        select: {
          id: true,
          ownerType: true,
          partnerId: true,
          registrationNumber: true,
          make: true,
          model: true,
          manufacturingYear: true,
          fuelType: true,
          transmission: true,
          seatingCapacity: true,
          status: true,
          createdAt: true,
          updatedAt: true,
        },
      }),
      prisma.vehicle.count({ where }),
    ]);

    return res.status(200).json({
      success: true,
      data: vehicles,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error("Admin vehicle-list error:", error);

    return res.status(500).json({
      success: false,
      message: "Unable to retrieve vehicles",
    });
  }
}
// Update vehicle details. Only the fields provided in the request body will be updated.
async function updateVehicle(req, res) {
  try {
    const { id } = req.params;

    // Validate the vehicle ID.
    if (
      typeof id !== "string" ||
      !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
        id
      )
    ) {
      return res.status(400).json({
        success: false,
        message: "Invalid vehicle ID",
      });
    }

    // Validate the request body.
    const validation = updateVehicleSchema.safeParse(req.body);

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

    // Check whether the vehicle exists.
    const existingVehicle = await prisma.vehicle.findUnique({
      where: { id },
      select: { id: true },
    });

    if (!existingVehicle) {
      return res.status(404).json({
        success: false,
        message: "Vehicle not found",
      });
    }

    // Update only the supplied fields.
    const updatedVehicle = await prisma.vehicle.update({
      where: { id },
      data,
      select: {
        id: true,
        ownerType: true,
        partnerId: true,
        registrationNumber: true,
        make: true,
        model: true,
        manufacturingYear: true,
        fuelType: true,
        transmission: true,
        seatingCapacity: true,
        status: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return res.status(200).json({
      success: true,
      message: "Vehicle updated successfully",
      data: updatedVehicle,
    });
  } catch (error) {
    if (error.code === "P2002") {
      return res.status(409).json({
        success: false,
        message: "Registration number already exists",
      });
    }

    console.error("Update vehicle error:", error);

    return res.status(500).json({
      success: false,
      message: "Unable to update vehicle",
    });
  }
}


module.exports = {
  createVehicle,
  listVehicles,
  getVehicleById,
  listAllVehicles,
  updateVehicle,
};



