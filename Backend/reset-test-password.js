require("dotenv").config();

const prisma = require("./src/lib/prisma");
const argon2 = require("argon2");

async function resetPassword() {
  const email = process.env.VROOM_RESET_EMAIL?.trim().toLowerCase();
  const newPassword = process.env.VROOM_RESET_PASSWORD;

  if (!email || !newPassword) {
    throw new Error("Email or new password is missing.");
  }

  if (newPassword.length < 8 || newPassword.length > 128) {
    throw new Error("Password must contain 8–128 characters.");
  }

  const user = await prisma.user.findUnique({
    where: { email },
    select: {
      id: true,
      email: true,
    },
  });

  if (!user) {
    throw new Error("No account found for that email address.");
  }

  const passwordHash = await argon2.hash(newPassword, {
    type: argon2.argon2id,
  });

  await prisma.user.update({
    where: { id: user.id },
    data: { passwordHash },
  });

  console.log("Password reset successful.");
  console.log("Account:", user.email);
  console.log("Your existing account and roles are unchanged.");
}

resetPassword()
  .catch((error) => {
    console.error("Password reset failed:", error.message);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
