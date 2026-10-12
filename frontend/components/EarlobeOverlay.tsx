"use client";

interface Point {
  x: number;
  y: number;
}

interface Props {
  earlobe: Point | null;
  earring: Point | null;
  earWidth: number;
  zoneYScale?: number;
  passThreshold: number;
  failThreshold: number;
  normalizedDistance?: number | null;
  showLandmarks: boolean;
  showEarring: boolean;
  showZone: boolean;
  showMeasurement: boolean;
}

export function EarlobeOverlay({
  earlobe,
  earring,
  earWidth,
  zoneYScale = 1,
  passThreshold,
  failThreshold,
  normalizedDistance,
  showLandmarks,
  showEarring,
  showZone,
  showMeasurement,
}: Props) {
  if (!earlobe) return null;
  const width = Math.max(earWidth, 0.01);
  const outerW = failThreshold * width * 2 * 100;
  const outerH = failThreshold * width * zoneYScale * 2 * 100;
  const innerW = passThreshold * width * 2 * 100;
  const innerH = passThreshold * width * zoneYScale * 2 * 100;
  return (
    <div className="pointer-events-none absolute inset-0">
      {showZone ? (
        <>
          <div
            className="absolute rounded-full border-2 border-yellow-400/80"
            style={{
              left: `${earlobe.x * 100 - outerW / 2}%`,
              top: `${earlobe.y * 100 - outerH / 2}%`,
              width: `${outerW}%`,
              height: `${outerH}%`,
            }}
          />
          <div
            className="absolute rounded-full border border-sky-300/80"
            style={{
              left: `${earlobe.x * 100 - innerW / 2}%`,
              top: `${earlobe.y * 100 - innerH / 2}%`,
              width: `${innerW}%`,
              height: `${innerH}%`,
            }}
          />
        </>
      ) : null}
      {showMeasurement && earring ? (
        <svg className="absolute inset-0 h-full w-full">
          <line
            x1={`${earlobe.x * 100}%`}
            y1={`${earlobe.y * 100}%`}
            x2={`${earring.x * 100}%`}
            y2={`${earring.y * 100}%`}
            stroke="#f8fafc"
            strokeWidth="2"
          />
          {normalizedDistance != null ? (
            <text
              x={`${((earlobe.x + earring.x) / 2) * 100}%`}
              y={`${((earlobe.y + earring.y) / 2) * 100}%`}
              fill="#f8fafc"
              fontSize="12"
            >
              {normalizedDistance.toFixed(3)}
            </text>
          ) : null}
        </svg>
      ) : null}
      {showLandmarks ? (
        <span
          title="Earlobe anchor"
          className="absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-emerald-400"
          style={{ left: `${earlobe.x * 100}%`, top: `${earlobe.y * 100}%` }}
        />
      ) : null}
      {showEarring && earring ? (
        <span
          title="Earring attachment anchor"
          className="absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-red-500"
          style={{ left: `${earring.x * 100}%`, top: `${earring.y * 100}%` }}
        />
      ) : null}
    </div>
  );
}
