const express = require("express");
const { createVehicle } = require("../controllers/vehicle.controller");
const requireAuth = require("../middleware/requireAuth");
const requireRole = require("../middleware/requireRole");

const router = express.Router();

// Only authenticated administrators can register vehicles.
router.post("/", requireAuth, requireRole("ADMIN"), createVehicle);

module.exports = router;
