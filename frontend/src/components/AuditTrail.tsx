import { useState } from "react";
import type { TraceStep } from "../types";

// "Show reasoning" — replays the deterministic algorithm step by step, so the
// pharmacist can check the tool's working. Collapsed by default.
const STATUS: Record<TraceStep["status"], { color: string; glyph: string }> = {
  ok: { color: "var(--color-clear)", glyph: "✓" },
  escalate: { color: "var(--color-stop)", glyph: "!" },
  block: { color: "var(--color-stop)", glyph: "✗" },
  info: { color: "var(--color-ink-muted)", glyph: "·" },
  skip: { color: "var(--color-rule)", glyph: "–" },
};

export function AuditTrail({ trace }: { trace: TraceStep[] }) {
  const [open, setOpen] = useState(false);
  if (trace.length === 0) return null;

  return (
    <div className="mt-8 border-t pt-4" style={{ borderColor: "var(--color-rule)" }}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="label flex items-center gap-1.5 transition-colors hover:text-[var(--color-ink)]"
      >
        <span className="mono inline-block w-2">{open ? "▾" : "▸"}</span>
        Show reasoning — {trace.length} deterministic steps
      </button>

      {open && (
        <ol className="relative mt-4 pl-1">
          {trace.map((s, i) => {
            const st = STATUS[s.status];
            const last = i === trace.length - 1;
            return (
              <li
                key={i}
                className="rail-stop relative flex gap-3 pb-4"
                style={{ animationDelay: `${i * 55}ms` }}
              >
                {!last && (
                  <span
                    className="absolute left-[11px] top-6 h-full w-px"
                    style={{ background: "var(--color-rule)" }}
                  />
                )}
                <span
                  className="mono relative z-10 flex h-[23px] w-[23px] shrink-0 items-center justify-center rounded-full border text-[11px]"
                  style={{ borderColor: st.color, color: st.color, background: "var(--color-paper)" }}
                >
                  {st.glyph}
                </span>
                <div className="min-w-0 flex-1 pt-0.5">
                  <div className="flex items-baseline gap-2">
                    <span className="mono text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
                      {String(s.step).padStart(2, "0")}
                    </span>
                    <span className="text-sm font-medium" style={{ color: st.color }}>
                      {s.name}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs leading-relaxed" style={{ color: "var(--color-ink)" }}>
                    {s.detail}
                  </p>
                  {s.items.length > 0 && (
                    <ul className="mono mt-1.5 space-y-0.5 text-[11px]" style={{ color: "var(--color-ink-muted)" }}>
                      {s.items.map((it, j) => (
                        <li key={j}>{it}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
