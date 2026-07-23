import { useEffect, useState } from "react";
import type { EvalCase } from "../types";
import { api } from "../api";
import { useLang } from "../LangContext";

// Table of the 30 cases with trap label. Clicking one loads it into the console.
export function EvalBrowser({ onLoad }: { onLoad: (c: EvalCase) => void }) {
  const { t } = useLang();
  const [cases, setCases] = useState<EvalCase[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.evalCases().then(setCases).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="label mb-3">{t("eval.title")}</div>
      {error && <p className="text-sm" style={{ color: "var(--color-stop)" }}>{error}</p>}
      <div className="panel overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="label border-b text-start" style={{ borderColor: "var(--color-rule)" }}>
              <th className="px-3 py-2 font-medium">{t("eval.id")}</th>
              <th className="px-3 py-2 font-medium">{t("eval.trap")}</th>
              <th className="px-3 py-2 font-medium">{t("eval.query")}</th>
              <th className="px-3 py-2 font-medium">{t("eval.expected")}</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr
                key={c.id}
                className="border-b transition-colors hover:bg-[var(--color-surface-2)]"
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
                    {c.must_escalate ? t("eval.escalate") : c.expected_tier}
                  </span>
                </td>
                <td className="px-3 py-2 text-end">
                  <button
                    onClick={() => onLoad(c)}
                    className="rounded-md border px-2.5 py-1 text-xs transition-colors hover:border-[var(--color-clear)] hover:text-[var(--color-clear)]"
                    style={{ borderColor: "var(--color-rule)", background: "var(--color-surface)" }}
                  >
                    {t("eval.run")}
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
