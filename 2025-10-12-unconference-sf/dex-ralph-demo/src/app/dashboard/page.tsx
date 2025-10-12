import { headers } from "next/headers";
import { redirect } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/auth";
import SignOutButton from "./sign-out-button";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center text-center max-w-2xl">
        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight">
          Dashboard
        </h1>

        <div className="w-full bg-black/[.05] dark:bg-white/[.06] rounded-lg p-6 sm:p-8">
          <p className="text-lg sm:text-xl text-foreground/80 mb-2">
            Welcome back!
          </p>
          <p className="font-mono text-sm sm:text-base text-foreground">
            {session.user.email}
          </p>
        </div>

        <div className="w-full flex flex-col gap-4">
          <h2 className="text-2xl font-semibold text-foreground">
            Jira Integration
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              href="/dashboard/jira"
              className="flex flex-col gap-2 p-6 rounded-lg border border-foreground/10 bg-black/[.02] dark:bg-white/[.03] hover:bg-black/[.05] dark:hover:bg-white/[.06] transition-colors"
            >
              <h3 className="text-lg font-semibold text-foreground">
                Jira Settings
              </h3>
              <p className="text-sm text-foreground/60">
                Configure your Jira connection and credentials
              </p>
            </Link>
            <Link
              href="/dashboard/jira/tickets"
              className="flex flex-col gap-2 p-6 rounded-lg border border-foreground/10 bg-black/[.02] dark:bg-white/[.03] hover:bg-black/[.05] dark:hover:bg-white/[.06] transition-colors"
            >
              <h3 className="text-lg font-semibold text-foreground">
                View Jira Tickets
              </h3>
              <p className="text-sm text-foreground/60">
                Browse and manage your Jira issues
              </p>
            </Link>
          </div>
        </div>

        <p className="text-foreground/60 text-sm sm:text-base">
          You are now signed in to Ralph PM Assistant. Your personalized
          dashboard for project management is coming soon.
        </p>

        <SignOutButton />
      </main>
    </div>
  );
}
