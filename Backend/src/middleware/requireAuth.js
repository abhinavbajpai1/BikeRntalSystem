const prisma = require("../lib/prisma");

async function requireAuth(req, res, next) {
  try {
    // 1. Check whether an authenticated session exists.
    if (!req.session || !req.session.userId) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    // 2. Verify that the user exists and is active.
const user = await prisma.user.findUnique({
  where: { id: req.session.userId },
  select: {
    id: true,
    isActive: true,
    roles: {
      select: {
        role: true,
      },
    },
  },
});

    if (!user || !user.isActive) {
      // Destroy the invalid session before rejecting the request.
      return req.session.destroy((err) => {
        if (err) {
          console.error("Invalid session cleanup error:", err);
        }

        res.clearCookie("vroom.sid", {
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
          sameSite: "lax",
          path: "/",
        });

        return res.status(401).json({
          success: false,
          message: "Your session is no longer valid",
        });
      });
    }

    // 3. Make the verified user available to later middleware/controllers.
   req.user = {
     id: user.id,
     roles: user.roles.map((item) => item.role),
   };

    return next();
  } catch (error) {
    console.error("Authentication middleware error:", error);

    return res.status(500).json({
      success: false,
      message: "Unable to verify authentication",
    });
  }
}

module.exports = requireAuth;
