import { RunStatus } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";

const LABELS: Record<string, string> = {
  application: "Application",
  authentication: "Authentication",
  capture: "Capture",
  frame_selection: "Layer 1 — Frame Selection",
  earlobe_detection: "Layer 2 — Earlobe Detection",
  earring_detection: "Layer 2 — Earring Anchor Detection",
  placement_validation: "Layer 3 — Placement Validation",
  report: "Report",
};

export function TestProgress({ status }: { status: RunStatus | null }) {
  if (!status) return null;
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-zinc-300">{status.stage_message}</p>
        <StatusBadge status={status.overall_status || status.status} />
      </div>
      <div className="h-2 overflow-hidden rounded bg-zinc-800">
        <div className="h-full bg-zinc-200" style={{ width: `${Math.max(0, Math.min(100, status.progress))}%` }} />
      </div>
      <ul className="space-y-2">
        {status.steps.map((step) => (
          <li key={step.name} className="flex items-center justify-between gap-3 text-sm">
            <span>
              <span className="text-zinc-200">{LABELS[step.name] || step.name}</span>
              {step.detail ? <span className="ml-2 text-zinc-500">{step.detail}</span> : null}
            </span>
            <StatusBadge status={step.status} />
          </li>
        ))}
      </ul>
      {status.reason ? <p className="text-sm text-zinc-300">{status.reason}</p> : null}
      {status.recommended_action ? <p className="text-sm text-zinc-500">Recommended action: {status.recommended_action}</p> : null}
    </div>
  );
}
