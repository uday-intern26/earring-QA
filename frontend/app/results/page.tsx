"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export default function ResultsPage() {
  const [runs, setRuns] = useState<Record<string, string | null>[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.runs()
      .then((items) => setRuns(items as Record<string, string | null>[]))
      .catch((exc: Error) => setError(exc.message));
  }, []);

  const finished = runs.filter((run) => run.overall_status);
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Latest Results</h2>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
      <ul className="space-y-3">
        {finished.map((run) => (
          <li key={String(run.test_run_id)} className="rounded border border-zinc-800 p-4">
            <div className="flex items-center justify-between">
              <Link className="underline" href={`/tests/${run.test_id}`}>
                {run.test_name}
              </Link>
              <StatusBadge status={run.overall_status} />
            </div>
            <p className="mt-1 text-xs text-zinc-500">{run.test_run_id}</p>
          </li>
        ))}
        {!finished.length ? <li className="text-sm text-zinc-500">No finished runs yet.</li> : null}
      </ul>
    </div>
  );
}
