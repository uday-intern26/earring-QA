"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export default function ReportsPage() {
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
      <h2 className="text-2xl font-semibold">Reports</h2>
      <p className="text-sm text-zinc-400">Download the JSON report for any completed run. Geometry, not pixel similarity, is the source of truth.</p>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
      <ul className="space-y-3">
        {finished.map((run) => (
          <li key={String(run.test_run_id)} className="flex items-center justify-between rounded border border-zinc-800 p-4">
            <div>
              <Link className="underline" href={`/tests/${run.test_id}`}>
                {run.test_name}
              </Link>
              <p className="mt-1 text-xs text-zinc-500">{run.test_run_id}</p>
            </div>
            <div className="flex items-center gap-3">
              <StatusBadge status={run.overall_status} />
              <a className="text-sm underline" href={api.reportUrl(String(run.test_id))}>
                Download
              </a>
            </div>
          </li>
        ))}
        {!finished.length ? <li className="text-sm text-zinc-500">No reports yet.</li> : null}
      </ul>
    </div>
  );
}
