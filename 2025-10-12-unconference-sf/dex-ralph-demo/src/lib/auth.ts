import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { magicLink } from "better-auth/plugins";
import { Resend } from "resend";
import prisma from "./prisma";

const resend = new Resend(process.env.RESEND_API_KEY);

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "sqlite",
  }),
  emailAndPassword: {
    enabled: false,
  },
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await resend.emails.send({
          from: process.env.EMAIL_FROM || "onboarding@resend.dev",
          to: email,
          subject: "Sign in to Ralph",
          html: `
            <h2>Sign in to Ralph</h2>
            <p>Click the link below to sign in to your account:</p>
            <a href="${url}" style="display: inline-block; padding: 12px 24px; background-color: #0070f3; color: white; text-decoration: none; border-radius: 5px; margin: 16px 0;">
              Sign In
            </a>
            <p>Or copy and paste this URL into your browser:</p>
            <p>${url}</p>
            <p>This link will expire in 5 minutes.</p>
            <p>If you didn't request this email, you can safely ignore it.</p>
          `,
        });
      },
      expiresIn: 60 * 5, // 5 minutes
    }),
  ],
});

export type Session = typeof auth.$Infer.Session;
