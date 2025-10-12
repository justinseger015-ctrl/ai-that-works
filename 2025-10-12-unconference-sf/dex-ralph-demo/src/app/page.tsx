import Link from "next/link";

export default function Home() {
  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center text-center">
        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight">
          Ralph PM Assistant
        </h1>
        <p className="text-lg sm:text-xl text-foreground/80 max-w-2xl">
          Your intelligent project management companion. Streamline your
          workflow and stay organized.
        </p>

        <div className="flex gap-4 items-center flex-col sm:flex-row mt-8">
          <Link
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]"
            href="/login"
          >
            Login
          </Link>
          <Link
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]"
            href="/dashboard"
          >
            Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
