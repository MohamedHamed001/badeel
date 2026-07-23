import { useEffect, useState } from "react";
import { api } from "../api";

interface Row {
  id: string;
  trap: string;
  correct: boolean;
  safety_ok: boolean;
  tier_ok: boolean;
  escalate_ok: boolean;
  recall_ok: boolean;
  flags_ok: boolean;
}

// Baseline "before" column (spec §1 / DECISIONS.md), for the before/after table.
const BASELINE = { label: "Naive baseline", correct: 0.0, safe: 83.3 };

export function Results() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [absent, setAbsent] = useState(false);

  useEffect(() => {
    api.evalResults().then((data) => {
      if (Array.isArray(data)) setRows(data as Row[]);
      else setAbsent(true);
    });
  }, []);

  if (absent)
    return (
      <div className="mx-auto max-w-4xl px-6 py-8">
        <p className="text-sm" style={{ color: "var(--color-ink-muted)" }}>
          No eval report yet. Run{" "}
          <span className="mono">python score.py predictions.jsonl</span> to
          generate one.
        </p>
      </div>
    );

  if (!rows) return <div className="px-6 py-8 label">Loading…</div>;

  const n = rows.length || 1;
  const pct = (k: keyof Row) => (100 * rows.filter((r) => r[k]).length) / n;

  const traps = [...new Set(rows.map((r) => r.trap))].sort();

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <div className="label mb-3">Results — before and after</div>

      <table className="w-full border text-sm" style={{ borderColor: "var(--color-rule)" }}>
        <thead>
          <tr className="label border-b text-left" style={{ borderColor: "var(--color-rule)" }}>
            <th className="px-3 py-2 font-medium">System</th>
            <th className="px-3 py-2 font-medium">Correct</th>
            <th className="px-3 py-2 font-medium">Safe</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b" style={{ borderColor: "var(--color-rule)" }}>
            <td className="px-3 py-2" style={{ color: "var(--color-ink-muted)" }}>{BASELINE.label}</td>
            <td className="mono px-3 py-2">{BASELINE.correct.toFixed(1)}%</td>
            <td className="mono px-3 py-2">{BASELINE.safe.toFixed(1)}%</td>
          </tr>
          <tr>
            <td className="px-3 py-2 font-medium">Badeel (current)</td>
            <td className="mono px-3 py-2" style={{ color: "var(--color-clear)" }}>
              {pct("correct").toFixed(1)}%
            </td>
            <td className="mono px-3 py-2" style={{ color: "var(--color-clear)" }}>
              {pct("safety_ok").toFixed(1)}%
            </td>
          </tr>
        </tbody>
      </table>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {(["tier_ok", "escalate_ok", "recall_ok", "flags_ok"] as const).map((k) => (
          <Metric key={k} label={k.replace("_ok", "")} value={pct(k)} />
        ))}
      </div>

      <div className="label mt-8 mb-2">Per-trap breakdown</div>
      <div className="overflow-x-auto border" style={{ borderColor: "var(--color-rule)" }}>
        <table className="w-full text-sm">
          <tbody>
            {traps.map((trap) => {
              const rs = rows.filter((r) => r.trap === trap);
              const ok = rs.filter((r) => r.correct).length;
              const safe = rs.filter((r) => r.safety_ok).length;
              return (
                <tr key={trap} className="border-b" style={{ borderColor: "var(--color-rule)" }}>
                  <td className="px-3 py-2 label normal-case">{trap.replace(/_/g, " ")}</td>
                  <td className="mono px-3 py-2 text-xs">{ok}/{rs.length} correct</td>
                  <td className="mono px-3 py-2 text-xs" style={{ color: safe === rs.length ? "var(--color-clear)" : "var(--color-stop)" }}>
                    {safe}/{rs.length} safe
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="border p-3" style={{ borderColor: "var(--color-rule)" }}>
      <div className="label">{label}</div>
      <div className="mono mt-1 text-lg">{value.toFixed(0)}%</div>
    </div>
  );
}
