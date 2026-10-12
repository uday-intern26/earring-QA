import { QaReport } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";
import { TestLayers, layerStatus } from "./TestLayers";

export function ResultSummary({ report }: { report: QaReport }) {
  const stats = report.statistics;
  const frameLayer = layerStatus(report.layers.frame_selection);
  const anchorLayer = layerStatus(report.layers.anchor_detection);
  const placementLayer = layerStatus(report.layers.placement_validation);
  const reference = report.reference_comparison;
  const actual = reference?.sides?.[0];
  const temporalEntries = Object.entries(report.temporal || {});
  return (
    <div className="space-y-6">
      <div className="grid gap-2 text-sm text-zinc-400 md:grid-cols-2">
        <p>Application: {report.application?.url || report.application?.name || "n/a"}</p>
        <p>
          Jewellery: {report.jewelry_id || "unspecified"} · {report.ear_side?.toUpperCase() || "n/a"}
        </p>
        <p>Run: {report.test_run_id}</p>
      </div>
      <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-6 text-center">
        <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Overall result</p>
        <div className="mt-3 flex justify-center">
          <StatusBadge status={report.overall_status} />
        </div>
        <div className="mt-6 grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <Metric label="Pass rate" value={stats ? `${(stats.pass_rate * 100).toFixed(1)}%` : "n/a"} />
          <Metric label="Frames tested" value={String(stats?.frames_selected ?? 0)} />
          <Metric label="Passed" value={String(stats?.frames_passed ?? 0)} />
          <Metric label="Failed" value={String(stats?.frames_failed ?? 0)} />
        </div>
        {report.reason ? <p className="mt-4 text-sm text-zinc-300">{report.reason}</p> : null}
        {report.recommended_action ? (
          <p className="mt-2 text-sm text-zinc-500">Recommended action: {report.recommended_action}</p>
        ) : null}
      </div>
      <div>
        <p className="mb-3 text-xs uppercase tracking-[0.2em] text-zinc-500">Three-layer validation</p>
        <TestLayers
          layers={[
            {
              title: "Layer 1 — Frame Selection",
              subtitle: "Select representative frames",
              status: frameLayer.status,
              detail: frameLayer.detail,
            },
            {
              title: "Layer 2 — Earlobe + Earring Anchor Detection",
              subtitle: "Locate both points",
              status: anchorLayer.status,
              detail: anchorLayer.detail,
            },
            {
              title: "Layer 3 — Placement Validation",
              subtitle: "PASS / WARNING / FAIL",
              status: placementLayer.status,
              detail: placementLayer.detail,
            },
          ]}
        />
      </div>
      {reference && reference.status !== "NOT_RUN" ? (
        <div className="rounded-lg border border-zinc-800 p-4 text-sm">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-zinc-200">Reference comparison</h3>
            <StatusBadge status={reference.status} />
          </div>
          <p className="mt-2 text-zinc-400">Reference distance: {actual?.magnitude_reference?.toFixed(3) ?? "n/a"}</p>
          <p className="text-zinc-400">Actual distance: {actual?.magnitude_actual?.toFixed(3) ?? "n/a"}</p>
          <p className="text-zinc-400">Difference: {actual?.distance_error?.toFixed(3) ?? "n/a"}</p>
          {actual?.angle_error != null ? <p className="text-zinc-400">Angle error: {actual.angle_error.toFixed(1)}°</p> : null}
          <p className="mt-2 text-zinc-500">{reference.reason}</p>
        </div>
      ) : null}
      {temporalEntries.length ? (
        <div className="rounded-lg border border-zinc-800 p-4 text-sm">
          <h3 className="mb-3 font-medium text-zinc-200">Temporal stability</h3>
          {temporalEntries.map(([side, summary]) => (
            <div key={side} className="mb-3 last:mb-0">
              <div className="flex items-center justify-between">
                <p className="capitalize text-zinc-300">{side} ear</p>
                <StatusBadge status={summary.status} />
              </div>
              <p className="mt-1 text-zinc-400">
                Pass rate {(summary.pass_rate * 100).toFixed(1)}% · Max consecutive failures {summary.max_consecutive_failures}{" "}
                · Allowed {report.thresholds.maximum_consecutive_failures}
              </p>
              <p className="text-zinc-500">{summary.reason}</p>
            </div>
          ))}
        </div>
      ) : null}
      <p className="text-xs text-zinc-500">
        Captured {stats?.frames_captured ?? 0} · Analyzed {stats?.frames_analyzed ?? 0} · Selected {stats?.frames_selected ?? 0} ·
        Warnings {stats?.frames_warning ?? 0} · Max consecutive failures {stats?.max_consecutive_failures ?? 0}
      </p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-1 text-xl text-zinc-100">{value}</p>
    </div>
  );
}
