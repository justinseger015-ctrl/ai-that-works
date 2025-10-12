"use client";

import Link from "next/link";
import { type FormEvent, useState } from "react";
import { authClient } from "@/lib/auth-client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await authClient.signIn.magicLink({
        email,
        callbackURL: "/dashboard",
      });

      if (response.error) {
        setError(response.error.message || "Failed to send magic link");
      } else {
        setIsSuccess(true);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-2">
            Welcome Back
          </h1>
          <p className="text-foreground/60 text-sm sm:text-base">
            Sign in to your account with a magic link
          </p>
        </div>

        <div className="bg-black/[.02] dark:bg-white/[.02] border border-black/[.08] dark:border-white/[.145] rounded-2xl p-6 sm:p-8">
          {isSuccess ? (
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-foreground/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  role="img"
                  aria-label="Email icon"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold mb-2">Check your email</h2>
              <p className="text-foreground/60 text-sm mb-6">
                We sent a magic link to{" "}
                <span className="font-medium text-foreground">{email}</span>
              </p>
              <p className="text-foreground/60 text-xs">
                Click the link in the email to sign in to your account
              </p>
              <button
                type="button"
                onClick={() => {
                  setIsSuccess(false);
                  setEmail("");
                }}
                className="mt-6 text-sm text-foreground/60 hover:text-foreground transition-colors underline underline-offset-4"
              >
                Use a different email
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium mb-2 text-foreground/80"
                >
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-4 py-3 rounded-lg bg-background border border-black/[.08] dark:border-white/[.145] focus:outline-none focus:ring-2 focus:ring-foreground/20 transition-all text-foreground placeholder:text-foreground/40"
                  disabled={isLoading}
                />
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-sm text-red-600 dark:text-red-400">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-full bg-foreground text-background font-medium text-sm sm:text-base h-11 sm:h-12 px-6 transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-foreground"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      role="img"
                      aria-label="Loading"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Sending magic link...
                  </span>
                ) : (
                  "Send magic link"
                )}
              </button>

              <div className="text-center">
                <p className="text-xs text-foreground/50">
                  By continuing, you agree to our Terms of Service and Privacy
                  Policy
                </p>
              </div>
            </form>
          )}
        </div>

        <div className="text-center mt-6">
          <Link
            href="/"
            className="text-sm text-foreground/60 hover:text-foreground transition-colors inline-flex items-center gap-1"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              role="img"
              aria-label="Back arrow"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
