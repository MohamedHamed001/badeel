import type { SafetyFlag } from "../types";

const SEVERITY_TONE: Record<string, string> = {
  major: "var(--color-stop)",
  moderate: "var(--color-caution)",
  minor: "var(--color-ink-muted)",
};

export function SafetyPanel({ flags }: { flags: SafetyFlag[] }) {
  if (flags.length === 0) return null;
  return (
    <div>
      <div className="label mb-2">Safety</div>
      <ul className="space-y-3">
        {flags.map((f, i) => (
          <li
            key={i}
            className="border-l-2 pl-3"
            style={{ borderColor: SEVERITY_TONE[f.severity] }}
          >
            <div className="flex items-baseline gap-2">
              <span className="label normal-case" style={{ color: SEVERITY_TONE[f.severity] }}>
                {f.kind.replace("_", " ")}
              </span>
              <span className="mono text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
                {f.severity}
              </span>
            </div>
            <p className="mt-0.5 text-xs leading-relaxed">{f.message}</p>
            {f.evidence.length > 0 && (
              <div className="mono mt-1 text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
                {f.evidence[0].leaflet} · {f.evidence[0].section}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
