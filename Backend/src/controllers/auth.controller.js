const argon2 = require("argon2");
const prisma = require("../lib/prisma");
const { registerSchema } = require("../validators/auth.validator");
const { loginSchema } = require("../validators/login.validator");

// Register a new user
async function register(req, res) {
  try {
    // 1. Validate request data
    const validation = registerSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        error: "Validation failed",
        details: validation.error.issues.map((issue) => ({
          field: issue.path.join("."),
          message: issue.message,
        })),
      });
    }

    const { name, email, password, phone } = validation.data;
    const normalizedPhone = phone || undefined;

    // 2. Check whether the email already exists
    const existingUser = await prisma.user.findUnique({
      where: { email },
      select: { id: true },
    });

    if (existingUser) {
      return res.status(409).json({
        error: "An account with this email already exists",
      });
    }

    // 3. Check phone uniqueness if provided
    if (normalizedPhone) {
      const existingPhone = await prisma.user.findUnique({
        where: { phone: normalizedPhone },
        select: { id: true },
      });

      if (existingPhone) {
        return res.status(409).json({
          error: "An account with this phone number already exists",
        });
      }
    }

    // 4. Hash the password using Argon2id
    const passwordHash = await argon2.hash(password, {
      type: argon2.argon2id,
    });

    // 5. Create the user and CUSTOMER role
    const user = await prisma.user.create({
      data: {
        name,
        email,
        passwordHash,
        ...(normalizedPhone ? { phone: normalizedPhone } : {}),
        roles: {
          create: {
            role: "CUSTOMER",
          },
        },
      },
      select: {
        id: true,
        name: true,
        email: true,
        phone: true,
        createdAt: true,
        roles: {
          select: {
            role: true,
          },
        },
      },
    });

    // 6. Return the user without the password hash
    return res.status(201).json({
      message: "Registration successful",
      user,
    });
  } catch (error) {
    console.error("Registration error details:", error);

    // Handle duplicate email or phone constraints
    if (error.code === "P2002") {
      return res.status(409).json({
        error: "An account with this email or phone number already exists",
      });
    }

    return res.status(500).json({
      error: "Internal server error",
    });
  }
}

// Login
async function login(req, res) {
  try {
    // 1. Validate request data
    const validation = loginSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        error: "Validation failed",
        details: validation.error.issues.map((issue) => ({
          field: issue.path.join("."),
          message: issue.message,
        })),
      });
    }

    const { email, password } = validation.data;

    // 2. Find the user by email
    const user = await prisma.user.findUnique({
      where: { email },
      include: {
        roles: {
          select: {
            role: true,
          },
        },
      },
    });

    // 3. Reject unknown or inactive accounts
    if (!user || !user.isActive) {
      return res.status(401).json({
        error: "Invalid email or password",
      });
    }

    // 4. Verify the password against its stored hash
    const passwordMatches = await argon2.verify(user.passwordHash, password);

    if (!passwordMatches) {
      return res.status(401).json({
        error: "Invalid email or password",
      });
    }

    // 5. Store the user in the session, then respond once it is saved.
    //    This callback is the ONLY place the response is sent.
    req.session.userId = user.id;

    return req.session.save((err) => {
      if (err) {
        console.error("Session save error:", err);

        return res.status(500).json({
          success: false,
          message: "Unable to establish a login session",
        });
      }

      return res.status(200).json({
        success: true,
        message: "Login successful",
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          phone: user.phone,
          roles: user.roles.map((item) => item.role),
        },
      });
    });
  } catch (error) {
    console.error("Login error details:", error);

    return res.status(500).json({
      error: "Internal server error",
    });
  }
}

// Current-user endpoint
async function getCurrentUser(req, res) {
  try {
    const user = await prisma.user.findUnique({
      where: {
        id: req.session.userId,
      },
      select: {
        id: true,
        name: true,
        email: true,
        phone: true,
        isActive: true,
        roles: {
          select: {
            role: true,
          },
        },
      },
    });

    if (!user || !user.isActive) {
      return req.session.destroy(() => {
        res.clearCookie("vroom.sid");

        return res.status(401).json({
          success: false,
          message: "Session is no longer valid",
        });
      });
    }

    return res.status(200).json({
      success: true,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        phone: user.phone,
        roles: user.roles.map((item) => item.role),
      },
    });
  } catch (error) {
    console.error("Get current user error:", error);

    return res.status(500).json({
      success: false,
      message: "Unable to retrieve current user",
    });
  }
}

// Logout
function logout(req, res) {
  if (!req.session) {
    return res.status(200).json({
      success: true,
      message: "Already logged out",
    });
  }

  req.session.destroy((err) => {
    if (err) {
      console.error("Logout session error:", err);

      return res.status(500).json({
        success: false,
        message: "Unable to log out",
      });
    }

    res.clearCookie("vroom.sid", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
    });

    return res.status(200).json({
      success: true,
      message: "Logout successful",
    });
  });
}

module.exports = { register, login, getCurrentUser, logout };
