"use client";

import { useEffect, useMemo, useState } from "react";

type TradingAccount = {
  accountId: string;
  type: string;
  kind: "demo" | "real";
  currency: string;
  balance: string;
  status?: string | null;
};

type MeResponse = {
  authenticated: boolean;
  user: {
    displayName: string;
    accountCount: number;
  } | null;
  accounts: {
    demo: TradingAccount[];
    real: TradingAccount[];
  };
  error?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5000";

export default function Home() {
  const [data, setData] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = Boolean(data?.authenticated);
  const totalBalance = useMemo(() => {
    const accounts = [...(data?.accounts.demo ?? []), ...(data?.accounts.real ?? [])];
    return accounts.reduce((sum, account) => {
      const value = Number.parseFloat(account.balance);
      return Number.isFinite(value) ? sum + value : sum;
    }, 0);
  }, [data]);

  useEffect(() => {
    void loadMe();
  }, []);

  async function loadMe() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/me`, {
        credentials: "include",
        cache: "no-store"
      });
      const body = (await response.json()) as MeResponse;

      if (!response.ok && response.status !== 401) {
        throw new Error(body.error || "Could not load your Deriv session.");
      }

      setData(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function login() {
    window.location.href = `${API_BASE_URL}/api/login`;
  }

  async function logout() {
    setLoggingOut(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/logout`, {
        method: "POST",
        credentials: "include"
      });
      if (!response.ok) {
        throw new Error("Logout failed.");
      }
      setData({
        authenticated: false,
        user: null,
        accounts: { demo: [], real: [] }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Logout failed.");
    } finally {
      setLoggingOut(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8">
        <header className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-coral">Fluxstrade</p>
            <h1 className="mt-3 text-4xl font-bold tracking-normal text-ink sm:text-5xl">
              Deriv Account Balances
            </h1>
          </div>

          {isAuthenticated ? (
            <button
              onClick={logout}
              disabled={loggingOut}
              className="inline-flex min-h-11 items-center justify-center rounded-md bg-ink px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-[#24385f] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loggingOut ? "Logging out..." : "Logout"}
            </button>
          ) : null}
        </header>

        {loading ? <LoadingState /> : null}

        {!loading && error ? (
          <div className="rounded-lg border border-red-200 bg-white p-5 text-red-700 shadow-soft">
            {error}
          </div>
        ) : null}

        {!loading && !isAuthenticated ? (
          <section className="grid gap-6 rounded-lg border border-white/80 bg-white/80 p-6 shadow-soft backdrop-blur md:grid-cols-[1.4fr_0.8fr] md:p-8">
            <div className="flex flex-col justify-center gap-4">
              <h2 className="text-2xl font-bold text-ink">Connect your Deriv account</h2>
              <p className="max-w-2xl text-base leading-7 text-slate-600">
                Sign in with Deriv to view your Demo and Real Options trading account balances in one
                private dashboard.
              </p>
            </div>
            <div className="flex items-center md:justify-end">
              <button
                onClick={login}
                className="inline-flex min-h-12 w-full items-center justify-center rounded-md bg-coral px-6 py-3 text-base font-bold text-white shadow-soft transition hover:bg-[#f25555] sm:w-auto"
              >
                Login with Deriv
              </button>
            </div>
          </section>
        ) : null}

        {!loading && isAuthenticated && data ? (
          <>
            <section className="grid gap-4 md:grid-cols-3">
              <SummaryCard label="Welcome" value={data.user?.displayName ?? "Deriv trader"} />
              <SummaryCard label="Accounts" value={String(data.user?.accountCount ?? 0)} />
              <SummaryCard label="Visible Balance" value={formatTotal(totalBalance)} />
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <AccountSection title="Demo Accounts" tone="mint" accounts={data.accounts.demo} />
              <AccountSection title="Real Accounts" tone="coral" accounts={data.accounts.real} />
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}

function LoadingState() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {[0, 1, 2].map((item) => (
        <div key={item} className="h-32 animate-pulse rounded-lg bg-white/80 shadow-soft" />
      ))}
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/80 bg-white/90 p-5 shadow-soft">
      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">{label}</p>
      <p className="mt-3 break-words text-2xl font-bold text-ink">{value}</p>
    </div>
  );
}

function AccountSection({
  title,
  tone,
  accounts
}: {
  title: string;
  tone: "mint" | "coral";
  accounts: TradingAccount[];
}) {
  const accent = tone === "mint" ? "bg-mint" : "bg-coral";

  return (
    <section className="rounded-lg border border-white/80 bg-white/90 p-5 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className={`h-3 w-3 rounded-full ${accent}`} />
          <h2 className="text-xl font-bold text-ink">{title}</h2>
        </div>
        <span className="rounded-md bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-600">
          {accounts.length}
        </span>
      </div>

      {accounts.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-200 p-6 text-sm text-slate-500">
          No accounts found in this section.
        </div>
      ) : (
        <div className="grid gap-4">
          {accounts.map((account) => (
            <article key={account.accountId} className="rounded-lg border border-slate-100 bg-white p-4">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-500">Account ID</p>
                  <p className="mt-1 break-all text-lg font-bold text-ink">{account.accountId}</p>
                </div>
                <div className="rounded-md bg-slate-50 px-3 py-2 text-left sm:text-right">
                  <p className="text-sm font-semibold text-slate-500">Balance</p>
                  <p className="mt-1 text-xl font-bold text-ink">
                    {account.balance} {account.currency}
                  </p>
                </div>
              </div>
              <div className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
                <Info label="Type" value={account.type} />
                <Info label="Currency" value={account.currency} />
                <Info label="Status" value={account.status ?? "N/A"} />
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-semibold text-slate-500">{label}</p>
      <p className="mt-1 break-words font-bold text-ink">{value}</p>
    </div>
  );
}

function formatTotal(value: number) {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}
