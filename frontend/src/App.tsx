import { useEffect, useState } from "react";
import { api } from "./api";
import type { EvalCase, Health, RegistryOptions, SubstitutionAnswer } from "./types";
import { SyntheticBanner } from "./components/SyntheticBanner";
import { Console } from "./views/Console";
import { EvalBrowser } from "./views/EvalBrowser";
import { Results } from "./views/Results";

type View = "console" | "eval" | "results";
type Query = { text: string; patient_flags: string[]; concurrent_meds: string[] };
const EMPTY: Query = { text: "", patient_flags: [], concurrent_meds: [] };

export default function App() {
  const [view, setView] = useState<View>("console");
  const [options, setOptions] = useState<RegistryOptions | null>(null);
  const [health, setHealth] = useState<Health | null>(null);

  const [query, setQuery] = useState<Query>(EMPTY);
  const [answer, setAnswer] = useState<SubstitutionAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.options().then(setOptions).catch(() => {});
    api.health().then(setHealth).catch(() => {});
  }, []);

  async function run(q: Query) {
    setLoading(true);
    setError(null);
    try {
      const a = await api.substitute(q);
      setAnswer(a);
    } catch (e) {
      setError(`Request failed: ${String(e)}`);
      setAnswer(null);
    } finally {
      setLoading(false);
    }
  }

  function loadCase(c: EvalCase) {
    const q: Query = {
      text: c.query_en,
      patient_flags: c.patient_flags,
      concurrent_meds: c.concurrent_meds,
    };
    setQuery(q);
    setView("console");
    run(q);
  }

  return (
    <div className="flex min-h-full flex-col">
      <SyntheticBanner />
      <Header view={view} setView={setView} health={health} />

      <main className="flex-1">
        {view === "console" && (
          <Console
            options={options}
            query={query}
            onChange={setQuery}
            onSubmit={() => run(query)}
            answer={answer}
            loading={loading}
            error={error}
          />
        )}
        {view === "eval" && <EvalBrowser onLoad={loadCase} />}
        {view === "results" && <Results />}
      </main>
    </div>
  );
}

function Header({
  view,
  setView,
  health,
}: {
  view: View;
  setView: (v: View) => void;
  health: Health | null;
}) {
  const tabs: { id: View; label: string }[] = [
    { id: "console", label: "Console" },
    { id: "eval", label: "Eval browser" },
    { id: "results", label: "Results" },
  ];
  return (
    <header
      className="flex items-center justify-between border-b px-6 py-3"
      style={{ borderColor: "var(--color-rule)" }}
    >
      <div className="flex items-baseline gap-6">
        <span className="text-base font-semibold tracking-tight">
          Badeel<span style={{ color: "var(--color-ink-muted)" }}> · بديل</span>
        </span>
        <nav className="flex gap-1">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setView(t.id)}
              className="px-2.5 py-1 text-sm"
              style={{
                color: view === t.id ? "var(--color-ink)" : "var(--color-ink-muted)",
                borderBottom: view === t.id ? "2px solid var(--color-ink)" : "2px solid transparent",
                fontWeight: view === t.id ? 600 : 400,
              }}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>
      {health && (
        <div className="mono hidden text-[10px] sm:block" style={{ color: "var(--color-ink-muted)" }}>
          {health.provider} · {health.model} · {health.chroma_docs} docs ·{" "}
          <span style={{ color: health.narration === "stubbed" ? "var(--color-caution)" : "var(--color-clear)" }}>
            narration {health.narration}
          </span>
        </div>
      )}
    </header>
  );
}
