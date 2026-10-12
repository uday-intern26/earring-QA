import { StatusBadge } from "./StatusBadge";

interface Layer {
  title: string;
  subtitle: string;
  status: string;
  detail?: string;
}

export function TestLayers({ layers }: { layers: Layer[] }) {
  return (
    <div className="space-y-3">
      {layers.map((layer, index) => (
        <div key={layer.title}>
          <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">{layer.title}</p>
                <p className="mt-1 text-sm text-zinc-200">{layer.subtitle}</p>
                {layer.detail ? <p className="mt-2 text-sm text-zinc-400">{layer.detail}</p> : null}
              </div>
              <StatusBadge status={layer.status} />
            </div>
          </div>
          {index < layers.length - 1 ? <div className="py-1 text-center text-zinc-600">↓</div> : null}
        </div>
      ))}
    </div>
  );
}

export function layerStatus(value: { status: string; detail: string } | string | undefined): { status: string; detail: string } {
  if (!value) return { status: "NOT_RUN", detail: "" };
  if (typeof value === "string") return { status: value, detail: "" };
  return value;
}
