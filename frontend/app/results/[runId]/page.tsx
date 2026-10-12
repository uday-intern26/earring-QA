"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

export default function RunRedirectPage() {
  const params = useParams<{ runId: string }>();
  const [testId, setTestId] = useState<string | null>(null);

  useEffect(() => {
    api.runs().then((items) => {
      const match = items.find((item) => item.test_run_id === params.runId);
      setTestId(match ? String(match.test_id) : null);
    });
  }, [params.runId]);

  if (!testId) {
    return <p className="text-sm text-zinc-400">Looking up {params.runId}.</p>;
  }
  return (
    <p className="text-sm">
      Open the test detail for this run: <Link className="underline" href={`/tests/${testId}`}>{testId}</Link>
    </p>
  );
}
