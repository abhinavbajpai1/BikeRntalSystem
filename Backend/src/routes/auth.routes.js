const express = require("express");
const { register, login, getCurrentUser,logout } = require("../controllers/auth.controller");
const requireAuth = require("../middleware/requireAuth");


const router = express.Router();

router.post("/register", register);

router.post("/login", login);

router.get("/me", requireAuth, getCurrentUser);

router.post("/logout",logout);

module.exports = router;
