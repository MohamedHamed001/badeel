import type { Substitute } from "../types";

const TIER_LABEL: Record<string, string> = {
  generic: "Generic",
  class: "Same class",
  therapeutic: "Therapeutic",
  none: "—",
};

export function SubstituteCard({ sub, rank }: { sub: Substitute; rank: number }) {
  const delta = sub.price_delta_pct;
  const deltaStr = `${delta > 0 ? "+" : ""}${delta.toFixed(0)}%`;

  return (
    <div
      className="border p-4 transition-colors hover:border-[var(--color-ink-muted)]"
      style={{ borderColor: "var(--color-rule)", background: "#fff" }}
    >
      <div className="flex items-baseline justify-between gap-3">
        <div className="flex items-baseline gap-2">
          <span className="mono text-[11px]" style={{ color: "var(--color-ink-muted)" }}>
            {String(rank).padStart(2, "0")}
          </span>
          <h3 className="text-base font-semibold">{sub.brand}</h3>
          <span className="text-sm" style={{ color: "var(--color-ink-muted)" }}>
            {sub.ingredient}
          </span>
        </div>
        <span className="label">{TIER_LABEL[sub.tier]}</span>
      </div>

      <div className="mono mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs" style={{ color: "var(--color-ink)" }}>
        <span>{sub.strength}</span>
        <span style={{ color: "var(--color-ink-muted)" }}>{sub.form}</span>
        <span>EGP {sub.price_egp.toFixed(2)}</span>
        {delta !== 0 && (
          <span style={{ color: delta > 0 ? "var(--color-caution)" : "var(--color-clear)" }}>
            {deltaStr}
          </span>
        )}
      </div>

      {sub.rationale && (
        <p className="mt-3 text-sm leading-relaxed">{sub.rationale}</p>
      )}

      {sub.counselling_flags.length > 0 && (
        <ul className="mt-3 space-y-1">
          {sub.counselling_flags.map((f, i) => (
            <li key={i} className="flex gap-2 text-xs" style={{ color: "var(--color-ink)" }}>
              <span style={{ color: "var(--color-caution)" }}>▸</span>
              <span>{f}</span>
            </li>
          ))}
        </ul>
      )}

      {sub.evidence.length > 0 && (
        <div className="label mt-3 flex flex-wrap gap-x-3 gap-y-1 normal-case">
          {sub.evidence.slice(0, 4).map((c, i) => (
            <span key={i} className="mono text-[10px]">
              {c.leaflet} · {c.section}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
