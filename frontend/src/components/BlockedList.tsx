import { useState } from "react";
import type { BlockedCandidate } from "../types";

// "Considered and rejected" — a collapsed disclosure for transparency.
export function BlockedList({ blocked }: { blocked: BlockedCandidate[] }) {
  const [open, setOpen] = useState(false);
  if (blocked.length === 0) return null;

  return (
    <div className="border-t pt-3" style={{ borderColor: "var(--color-rule)" }}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="label flex items-center gap-1.5"
      >
        <span className="mono">{open ? "▾" : "▸"}</span>
        Considered and rejected ({blocked.length})
      </button>
      {open && (
        <ul className="mt-2 space-y-2">
          {blocked.map((b, i) => (
            <li key={i} className="flex items-baseline gap-2 text-xs">
              <span
                className="line-through"
                style={{ color: "var(--color-ink-muted)", textDecorationColor: "var(--color-stop)" }}
              >
                {b.brand ?? b.ingredient}
              </span>
              <span className="mono text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
                {b.ingredient}
              </span>
              <span style={{ color: "var(--color-ink-muted)" }}>— {b.reason}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
