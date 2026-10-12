"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const GROUPS = [
  {
    title: null,
    links: [{ href: "/", label: "Dashboard" }],
  },
  {
    title: "Setup",
    links: [{ href: "/applications", label: "Applications" }],
  },
  {
    title: "Tests",
    links: [
      { href: "/tests", label: "Test Configurations" },
      { href: "/tests/runs", label: "Test Runs" },
    ],
  },
  {
    title: "Results",
    links: [
      { href: "/results", label: "Latest Results" },
      { href: "/reports", label: "Reports" },
    ],
  },
  {
    title: null,
    links: [{ href: "/settings", label: "Settings" }],
  },
];

export function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-zinc-800 bg-zinc-950 px-4 py-6">
        <div className="px-2">
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">AIJewel QA</p>
          <h1 className="mt-1 text-lg font-semibold text-zinc-100">Try-On QA</h1>
        </div>
        <nav className="mt-8 space-y-5">
          {GROUPS.map((group, index) => (
            <div key={group.title || `group-${index}`}>
              {group.title ? (
                <p className="mb-1 px-3 text-[11px] uppercase tracking-[0.18em] text-zinc-600">{group.title}</p>
              ) : null}
              <div className="space-y-1">
                {group.links.map((link) => {
                  const active = pathname === link.href;
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={`block rounded px-3 py-2 text-sm ${
                        active ? "bg-zinc-800 text-white" : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                      }`}
                    >
                      {link.label}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </aside>
      <main className="flex-1 px-8 py-6">{children}</main>
    </div>
  );
}

export function Card({ title, children, step }: { title?: string; children: ReactNode; step?: string }) {
  return (
    <section className="rounded-lg border border-zinc-800 bg-zinc-900/70 p-5">
      {title ? (
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-zinc-300">
          {step ? <span className="mr-2 text-zinc-500">{step}</span> : null}
          {title}
        </h2>
      ) : null}
      {children}
    </section>
  );
}

export function Field({ label, children }: { children: ReactNode; label: string }) {
  return (
    <label className="block space-y-1 text-sm">
      <span className="text-zinc-400">{label}</span>
      {children}
    </label>
  );
}

export const inputClass =
  "w-full rounded border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm outline-none focus:border-zinc-500";
