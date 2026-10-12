"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export default function RunsPage() {
  const [runs, setRuns] = useState<Record<string, string | number | null>[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.runs()
      .then((items) => setRuns(items as Record<string, string | number | null>[]))
      .catch((exc: Error) => setError(exc.message));
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Test Runs</h2>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
      <table className="w-full text-left text-sm">
        <thead className="text-xs uppercase text-zinc-500">
          <tr>
            <th className="py-2">Run</th>
            <th>Test</th>
            <th>Status</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={String(run.test_run_id)} className="border-t border-zinc-800">
              <td className="py-2">{run.test_run_id}</td>
              <td>
                <Link className="underline" href={`/tests/${run.test_id}`}>
                  {run.test_name}
                </Link>
              </td>
              <td>{run.status}</td>
              <td>
                <StatusBadge status={String(run.overall_status || "NOT_RUN")} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
