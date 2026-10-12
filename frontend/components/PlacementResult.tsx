import { FrameRow } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";

export function PlacementResult({
  frames,
  activeId,
  activeSide,
  onSelect,
}: {
  frames: FrameRow[];
  activeId?: string;
  activeSide?: string;
  onSelect: (frame: FrameRow) => void;
}) {
  if (!frames.length) {
    return <p className="text-sm text-zinc-500">No frame-level placement results.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="text-xs uppercase tracking-wide text-zinc-500">
          <tr>
            <th className="py-2">Frame</th>
            <th>Time</th>
            <th>Side</th>
            <th>Earlobe</th>
            <th>Earring</th>
            <th>Distance</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {frames.map((frame) => {
            const active = frame.frame_id === activeId && frame.side === activeSide;
            return (
              <tr
                key={`${frame.frame_id}-${frame.side}`}
                className={`cursor-pointer border-t border-zinc-800 ${
                  active ? "bg-zinc-800/70" : frame.status === "FAIL" ? "bg-red-950/40 hover:bg-red-950/60" : "hover:bg-zinc-900"
                }`}
                onClick={() => onSelect(frame)}
              >
                <td className="py-2">{String(frame.frame_number).padStart(3, "0")}</td>
                <td>{(frame.timestamp_ms / 1000).toFixed(1)}s</td>
                <td>{frame.side}</td>
                <td>{frame.earlobe_detected ? "✓" : "✗"}</td>
                <td>{frame.earring_detected ? "✓" : "✗"}</td>
                <td>{frame.normalized_distance?.toFixed(3) ?? "—"}</td>
                <td>
                  <StatusBadge status={frame.status} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
