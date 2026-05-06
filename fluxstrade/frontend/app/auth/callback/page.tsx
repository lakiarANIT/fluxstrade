"use client";

import { Suspense, useEffect, useMemo } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

export default function AuthCallbackPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-8">
      <Suspense fallback={<CallbackShell message="Finishing Deriv login..." />}>
        <AuthCallbackContent />
      </Suspense>
    </main>
  );
}

function AuthCallbackContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");
  const success = searchParams.get("success");

  const message = useMemo(() => {
    if (error) {
      return error;
    }
    if (success) {
      return "Deriv login successful. Returning to your dashboard...";
    }
    return "Finishing Deriv login...";
  }, [error, success]);

  useEffect(() => {
    if (!error) {
      const timeout = window.setTimeout(() => {
        window.location.href = "/";
      }, 700);
      return () => window.clearTimeout(timeout);
    }
  }, [error]);

  return (
    <CallbackShell message={message} title={error ? "Login failed" : "Login complete"}>
      {error ? (
        <Link
          href="/"
          className="mt-6 inline-flex min-h-11 items-center justify-center rounded-md bg-ink px-5 py-3 text-sm font-semibold text-white"
        >
          Back to dashboard
        </Link>
      ) : null}
    </CallbackShell>
  );
}

function CallbackShell({
  title = "Login complete",
  message,
  children
}: {
  title?: string;
  message: string;
  children?: React.ReactNode;
}) {
  return (
    <section className="w-full max-w-md rounded-lg border border-white/80 bg-white p-6 text-center shadow-soft">
      <p className="text-sm font-semibold uppercase tracking-[0.22em] text-coral">Fluxstrade</p>
      <h1 className="mt-3 text-2xl font-bold text-ink">{title}</h1>
      <p className="mt-4 leading-7 text-slate-600">{message}</p>
      {children}
    </section>
  );
}
