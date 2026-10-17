"use client";

import { useState } from "react";
import { api, FrameRow } from "@/lib/api";
import { EarlobeOverlay } from "./EarlobeOverlay";
import { StatusBadge } from "./StatusBadge";

interface Props {
  frame: FrameRow | null;
  passThreshold: number;
  failThreshold: number;
  zoneYScale?: number;
  reference?: {
    imageUrl: string;
    earlobe: { x: number; y: number } | null;
    earring: { x: number; y: number } | null;
    earWidth: number;
    distance: number | null;
  } | null;
}

export function FrameViewer({ frame, passThreshold, failThreshold, zoneYScale = 1, reference }: Props) {
  const [showLandmarks, setShowLandmarks] = useState(false);
  const [showEarring, setShowEarring] = useState(false);
  const [showZone, setShowZone] = useState(false);
  const [showMeasurement, setShowMeasurement] = useState(false);
  const [annotated, setAnnotated] = useState(false);

  if (!frame) {
    return <p className="text-sm text-zinc-500">Select a frame to inspect the earlobe and earring anchors.</p>;
  }

  const image = annotated && frame.annotated_image_url ? frame.annotated_image_url : frame.image_url;

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_280px]">
      <div>
        <div className="relative inline-block max-w-full overflow-hidden rounded border border-zinc-800 bg-black">
          <img src={api.asset(image)} alt={`Frame ${frame.frame_number}`} className="max-h-[520px] w-full object-contain" />
          {!annotated ? (
            <EarlobeOverlay
              earlobe={frame.earlobe}
              earring={frame.earring}
              earWidth={frame.zone?.ear_width || 0.05}
              zoneYScale={zoneYScale}
              passThreshold={passThreshold}
              failThreshold={failThreshold}
              normalizedDistance={frame.normalized_distance}
              showLandmarks={showLandmarks}
              showEarring={showEarring}
              showZone={showZone}
              showMeasurement={showMeasurement}
            />
          ) : null}
        </div>
        <div className="mt-3 flex flex-wrap gap-3 text-sm text-zinc-300">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={showLandmarks} onChange={(event) => setShowLandmarks(event.target.checked)} />
            Show landmarks
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={showEarring} onChange={(event) => setShowEarring(event.target.checked)} />
            Show earring anchor
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={showZone} onChange={(event) => setShowZone(event.target.checked)} />
            Show placement zone
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={showMeasurement} onChange={(event) => setShowMeasurement(event.target.checked)} />
            Show measurement
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={annotated} onChange={(event) => setAnnotated(event.target.checked)} />
            Server annotated image
          </label>
        </div>
        {reference?.imageUrl ? (
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <figure>
              <figcaption className="mb-2 text-xs uppercase tracking-wide text-zinc-500">Reference</figcaption>
              <div className="relative overflow-hidden rounded border border-zinc-800">
                <img src={reference.imageUrl} alt="Reference" className="w-full object-contain" />
                <EarlobeOverlay
                  earlobe={reference.earlobe}
                  earring={reference.earring}
                  earWidth={reference.earWidth || 0.05}
                  zoneYScale={zoneYScale}
                  passThreshold={passThreshold}
                  failThreshold={failThreshold}
                  normalizedDistance={reference.distance}
                  showLandmarks
                  showEarring
                  showZone={false}
                  showMeasurement
                />
              </div>
              <p className="mt-2 text-sm text-zinc-400">Reference distance: {reference.distance?.toFixed(3) ?? "n/a"}</p>
            </figure>
            <figure>
              <figcaption className="mb-2 text-xs uppercase tracking-wide text-zinc-500">Actual</figcaption>
              <div className="relative overflow-hidden rounded border border-zinc-800">
                <img src={api.asset(frame.image_url)} alt="Actual frame" className="w-full object-contain" />
                <EarlobeOverlay
                  earlobe={frame.earlobe}
                  earring={frame.earring}
                  earWidth={frame.zone?.ear_width || 0.05}
                  zoneYScale={zoneYScale}
                  passThreshold={passThreshold}
                  failThreshold={failThreshold}
                  normalizedDistance={frame.normalized_distance}
                  showLandmarks={showLandmarks}
                  showEarring={showEarring}
                  showZone={showZone}
                  showMeasurement={showMeasurement}
                />
              </div>
              <p className="mt-2 text-sm text-zinc-300">Actual distance: {frame.normalized_distance?.toFixed(3) ?? "n/a"}</p>
              <p className="text-sm text-zinc-300">
                Difference:{" "}
                {frame.normalized_distance != null && reference.distance != null
                  ? (frame.normalized_distance - reference.distance).toFixed(3)
                  : "n/a"}
              </p>
            </figure>
          </div>
        ) : null}
      </div>
      <aside className="space-y-2 rounded border border-zinc-800 bg-zinc-950 p-4 text-sm">
        <p className="text-zinc-400">Frame {String(frame.frame_number).padStart(3, "0")}</p>
        <p>Timestamp: {(frame.timestamp_ms / 1000).toFixed(1)}s</p>
        <p>Side: {frame.side}</p>
        <p>Earlobe confidence: {frame.earlobe_confidence?.toFixed(2) ?? "n/a"}</p>
        <p>Earring confidence: {frame.earring_confidence?.toFixed(2) ?? "n/a"}</p>
        <p>Normalized distance: {frame.normalized_distance?.toFixed(3) ?? "n/a"}</p>
        <p>Allowed: &lt;= {failThreshold.toFixed(2)}</p>
        <p>
          Earlobe: {frame.earlobe ? `${frame.earlobe.x.toFixed(3)}, ${frame.earlobe.y.toFixed(3)}` : "not detected"}
        </p>
        <p>
          Earring: {frame.earring ? `${frame.earring.x.toFixed(3)}, ${frame.earring.y.toFixed(3)}` : "not detected"}
        </p>
        <p className="pt-2">
          <StatusBadge status={frame.automated_result} />
        </p>
        <p className="text-zinc-300">{frame.reason}</p>
        {frame.manual_result ? (
          <p className="text-zinc-400">
            Manual review {frame.manual_result} by {frame.reviewer}. Automated result stays {frame.automated_result}.{" "}
            {frame.review_reason}
          </p>
        ) : null}
      </aside>
    </div>
  );
}
