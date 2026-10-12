require("dotenv").config();

const express = require("express");
const { Pool } = require("pg");
const prisma = require("./src/lib/prisma");
const authRoutes = require("./src/routes/auth.routes");

const app = express();
const PORT = Number(process.env.PORT) || 4000;

// Parse incoming JSON requests.
app.use(express.json());
app.use("/api/auth", authRoutes);

// PostgreSQL connection pool.
const pool = new Pool({
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

// Log unexpected database connection errors.
pool.on("error", (error) => {
  console.error("Unexpected PostgreSQL pool error:", error.message);
});

// API health check.
app.get("/api/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    service: "Vroom Vroom API",
  });
});

app.get("/api/health/prisma", async (req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;

    res.status(200).json({
      status: "ok",
      database: "connected",
      orm: "Prisma",
    });
  } catch (error) {
    console.error("Prisma health check failed:", error.message);

    res.status(503).json({
      status: "error",
      database: "disconnected",
    });
  }
});

// Database health check.
app.get("/api/health/db", async (req, res) => {
  try {
    await pool.query("SELECT 1");

    res.status(200).json({
      status: "ok",
      database: "connected",
    });
  } catch (error) {
    console.error("Database health check failed:", error.message);

    res.status(503).json({
      status: "error",
      database: "disconnected",
    });
  }
});

// Handle unknown routes.
app.use((req, res) => {
  res.status(404).json({
    error: "Route not found",
  });
});

// Handle unexpected request errors.
app.use((err, req, res, next) => {
  console.error("Request error:", err.message);

  if (res.headersSent) {
    return next(err);
  }

  res.status(500).json({
    error: "Internal server error",
  });
});

// Start the API server.
const server = app.listen(PORT, () => {
  console.log(`Vroom Vroom API running on http://localhost:${PORT}`);
});

// Gracefully close connections when the server stops.
let shuttingDown = false;

function shutdown(signal) {
  if (shuttingDown) {
    return;
  }

  shuttingDown = true;
  console.log(`${signal} received. Shutting down...`);

  server.close(async () => {
    try {
      await pool.end();
      console.log("Database connections closed.");
      process.exitCode = 0;
    } catch (error) {
      console.error("Error closing database connections:", error.message);
      process.exitCode = 1;
    }
  });
}

process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));
