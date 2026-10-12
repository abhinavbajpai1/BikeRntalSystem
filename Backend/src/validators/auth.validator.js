const { z } = require("zod");

const registerSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, "Name must contain at least 2 characters")
    .max(100, "Name cannot exceed 100 characters"),

  email: z
    .string()
    .trim()
    .email("Enter a valid email address")
    .max(255, "Email cannot exceed 255 characters")
    .transform((value) => value.toLowerCase()),

  password: z
    .string()
    .min(8, "Password must contain at least 8 characters")
    .max(128, "Password cannot exceed 128 characters"),

  phone: z
    .string()
    .trim()
    .min(7, "Phone number is too short")
    .max(20, "Phone number is too long")
    .optional()
    .or(z.literal("")),
});

module.exports = { registerSchema };
