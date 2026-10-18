const express = require("express");

const {
  createVehicle,
  listVehicles,
  getVehicleById,
  listAllVehicles,
  updateVehicle,
} = require("../controllers/vehicle.controller");

const requireAuth = require("../middleware/requireAuth");
const requireRole = require("../middleware/requireRole");

const router = express.Router();

// Public: list active vehicles
router.get("/", listVehicles);

// Admin: manage all vehicles
router.get(
  "/manage",
  requireAuth,
  requireRole("ADMIN"),
  listAllVehicles
);

// Public: retrieve a single active vehicle
router.get("/:id", getVehicleById);

// Admin: create a vehicle
router.post(
  "/",
  requireAuth,
  requireRole("ADMIN"),
  createVehicle
);

// Admin: update vehicle details
router.patch(
  "/:id",
  requireAuth,
  requireRole("ADMIN"),
  updateVehicle
);

module.exports = router;

