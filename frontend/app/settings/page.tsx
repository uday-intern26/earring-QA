"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.settings().then(setSettings).catch((exc: Error) => setError(exc.message));
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Settings</h2>
      <p className="max-w-2xl text-sm text-zinc-400">
        Thresholds and the optional Applitools key come from the environment. Applitools never decides whether the
        earring attachment sits on the earlobe. That decision uses the earlobe anchor and the earring attachment anchor.
      </p>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
      <pre className="overflow-auto rounded border border-zinc-800 bg-zinc-950 p-4 text-xs text-zinc-300">
        {JSON.stringify(settings, null, 2)}
      </pre>
    </div>
  );
}
