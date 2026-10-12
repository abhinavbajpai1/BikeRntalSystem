const prisma = require("./src/lib/prisma");

console.log("DATABASE_URL loaded:", Boolean(process.env.DATABASE_URL));

console.log(
  "DATABASE_URL has password:",
  (() => {
    try {
      return Boolean(new URL(process.env.DATABASE_URL).password);
    } catch {
      return false;
    }
  })(),
);

async function main() {
  await prisma.$connect();

  const result = await prisma.$queryRaw`SELECT 1 AS connected`;

  console.log("Prisma connected successfully:", result);
}

main()
  .catch((error) => {
    console.error("Prisma connection failed:", error.message);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
