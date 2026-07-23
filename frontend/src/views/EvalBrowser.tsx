import { useEffect, useState } from "react";
import type { EvalCase } from "../types";
import { api } from "../api";

// Table of the 30 cases with trap label. Clicking one loads it into the console.
export function EvalBrowser({ onLoad }: { onLoad: (c: EvalCase) => void }) {
  const [cases, setCases] = useState<EvalCase[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.evalCases().then(setCases).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="label mb-3">Adversarial eval — 30 labelled cases</div>
      {error && <p className="text-sm" style={{ color: "var(--color-stop)" }}>{error}</p>}
      <div className="overflow-x-auto border" style={{ borderColor: "var(--color-rule)" }}>
        <table className="w-full text-sm">
          <thead>
            <tr className="label border-b text-left" style={{ borderColor: "var(--color-rule)" }}>
              <th className="px-3 py-2 font-medium">ID</th>
              <th className="px-3 py-2 font-medium">Trap</th>
              <th className="px-3 py-2 font-medium">Query</th>
              <th className="px-3 py-2 font-medium">Expected</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr
                key={c.id}
                className="border-b hover:bg-white"
                style={{ borderColor: "var(--color-rule)" }}
              >
                <td className="mono px-3 py-2 text-xs">{c.id}</td>
                <td className="px-3 py-2">
                  <span className="label normal-case">{c.trap.replace(/_/g, " ")}</span>
                </td>
                <td className="px-3 py-2" style={{ color: "var(--color-ink-muted)" }}>
                  {c.query_en}
                </td>
                <td className="px-3 py-2">
                  <span
                    className="mono text-xs"
                    style={{ color: c.must_escalate ? "var(--color-stop)" : "var(--color-ink)" }}
                  >
                    {c.must_escalate ? "escalate" : c.expected_tier}
                  </span>
                </td>
                <td className="px-3 py-2 text-right">
                  <button
                    onClick={() => onLoad(c)}
                    className="border px-2 py-1 text-xs"
                    style={{ borderColor: "var(--color-rule)" }}
                  >
                    Run →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
