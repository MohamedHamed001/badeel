import { useEffect, useRef, useState } from "react";
import { api, substituteStream } from "./api";
import type { Dataset } from "./api";
import type { EvalCase, Health, RegistryOptions, SubstitutionAnswer } from "./types";
import type { Lang } from "./i18n";
import { makeT } from "./i18n";
import { LangProvider, useLang } from "./LangContext";
import { SyntheticBanner } from "./components/SyntheticBanner";
import { Console } from "./views/Console";
import { EvalBrowser } from "./views/EvalBrowser";
import { Results } from "./views/Results";

type View = "console" | "eval" | "results";
type Query = { text: string; patient_flags: string[]; concurrent_meds: string[] };
const EMPTY: Query = { text: "", patient_flags: [], concurrent_meds: [] };

export default function App() {
  const [lang, setLangState] = useState<Lang>("en");
  const [view, setView] = useState<View>("console");
  const [options, setOptions] = useState<RegistryOptions | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  // Which drug universe the console is working in. Starts as whatever the
  // server defaults to, then the user can switch live.
  const [dataset, setDatasetState] = useState<Dataset | null>(null);

  const [query, setQuery] = useState<Query>(EMPTY);
  const [answer, setAnswer] = useState<SubstitutionAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastRun = useRef<Query | null>(null);

  const dir = lang === "ar" ? "rtl" : "ltr";

  useEffect(() => {
    document.documentElement.dir = dir;
    document.documentElement.lang = lang;
  }, [dir, lang]);

  useEffect(() => {
    api.health()
      .then((h) => {
        setHealth(h);
        setDatasetState((d) => d ?? (h.dataset as Dataset));
      })
      .catch(() => {});
  }, []);

  // Reload the ingredient chips whenever the dataset changes — the concurrent
  // meds list is different in each build.
  useEffect(() => {
    api.options(dataset ?? undefined).then(setOptions).catch(() => {});
  }, [dataset]);

  function setDataset(d: Dataset) {
    if (d === dataset) return;
    setDatasetState(d);
    // The showing result came from the other drug universe, so it is no longer
    // meaningful. Clear rather than silently leaving a stale verdict on screen.
    setAnswer(null);
    setError(null);
    setQuery(EMPTY);
    lastRun.current = null;
  }

  async function run(q: Query, l: Lang = lang, ds: Dataset | null = dataset) {
    lastRun.current = q;
    setLoading(true);
    setError(null);
    setAnswer(null);

    // Buffer the whole response and reveal it ONCE, complete with rationale —
    // the user sees a single loading state, then the finished result. No
    // partial render, no text that appears then changes.
    let pending: SubstitutionAnswer | null = null;
    let done = false;
    const reveal = (a: SubstitutionAnswer) => {
      setAnswer(a);
      setLoading(false);
      done = true;
    };

    await substituteStream(
      { ...q, lang: l, ...(ds ? { dataset: ds } : {}) },
      {
        onAnswer: (a) => {
          pending = a;
        },
        onNarrating: () => {},
        onDelta: () => {},
        onDone: (i, d) => {
          if (!pending) return;
          reveal({
            ...pending,
            guard_trips: pending.guard_trips + (d.guard_trip ? 1 : 0),
            model_used: d.model ?? pending.model_used, // the LLM actually ran
            latency_ms: d.latency_ms ?? pending.latency_ms,
            substitutes: pending.substitutes.map((s, idx) =>
              idx === i
                ? { ...s, rationale: d.rationale, evidence: (d.evidence as typeof s.evidence) ?? s.evidence }
                : s,
            ),
          });
        },
        onError: (e) => {
          setError(`Request failed: ${e}`);
          setAnswer(null);
          setLoading(false);
          done = true;
        },
      },
    );
    // escalations / narration-off: no `done` event, reveal the buffered answer
    if (!done && pending) reveal(pending);
    setLoading(false);
  }

  function setLang(l: Lang) {
    setLangState(l);
    if (lastRun.current && answer) run(lastRun.current, l); // re-render content in new language
  }

  function loadCase(c: EvalCase) {
    const q: Query = {
      text: c.query_en,
      patient_flags: c.patient_flags,
      concurrent_meds: c.concurrent_meds,
    };
    // Eval cases name synthetic drugs, so they must always be answered from the
    // synthetic build — otherwise "Atorex" would be meaningless in real mode.
    // Switch the console over too, so what is on screen matches what ran.
    setDatasetState("synthetic");
    setQuery(q);
    setView("console");
    run(q, lang, "synthetic");
  }

  return (
    <LangProvider value={{ lang, dir, t: makeT(lang), setLang }}>
      <div className="flex min-h-full flex-col">
        <SyntheticBanner />
        <Header view={view} setView={setView} health={health}
                dataset={dataset} setDataset={setDataset} />

        <main className="flex-1">
          {view === "console" && (
            <Console
              options={options}
              dataset={dataset ?? "synthetic"}
              query={query}
              onChange={setQuery}
              onSubmit={() => run(query)}
              onExample={(q) => {
                setQuery(q);
                run(q);
              }}
              answer={answer}
              loading={loading}
              error={error}
            />
          )}
          {view === "eval" && <EvalBrowser onLoad={loadCase} />}
          {view === "results" && <Results />}
        </main>
      </div>
    </LangProvider>
  );
}

function Header({
  view,
  setView,
  health,
  dataset,
  setDataset,
}: {
  view: View;
  setView: (v: View) => void;
  health: Health | null;
  dataset: Dataset | null;
  setDataset: (d: Dataset) => void;
}) {
  const { t, lang, setLang } = useLang();
  const tabs: { id: View; key: Parameters<typeof t>[0] }[] = [
    { id: "console", key: "nav.console" },
    { id: "eval", key: "nav.eval" },
    { id: "results", key: "nav.results" },
  ];
  return (
    <header
      className="flex items-center justify-between border-b px-6 py-3"
      style={{ borderColor: "var(--color-rule)", background: "var(--color-paper)" }}
    >
      <div className="flex items-center gap-6">
        <span className="text-base font-bold tracking-tight">
          Badeel<span className="font-normal" style={{ color: "var(--color-ink-muted)" }}> · بديل</span>
        </span>
        <nav className="flex gap-1">
          {tabs.map((tab) => {
            const on = view === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setView(tab.id)}
                className="rounded-md px-3 py-1.5 text-sm transition-colors"
                style={{
                  color: on ? "var(--color-ink)" : "var(--color-ink-muted)",
                  background: on ? "var(--color-surface-2)" : "transparent",
                  fontWeight: on ? 600 : 400,
                }}
              >
                {t(tab.key)}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="flex items-center gap-3">
        {/* Dataset switch. The two drug universes stay completely separate —
            this picks which one answers, it never merges them. */}
        <div
          className="flex overflow-hidden rounded-md border"
          style={{ borderColor: "var(--color-rule)" }}
        >
          {(["synthetic", "real"] as Dataset[]).map((d) => {
            const on = dataset === d;
            return (
              <button
                key={d}
                onClick={() => setDataset(d)}
                className="mono px-2.5 py-1 text-[10px] font-semibold transition-colors"
                style={{
                  background: on
                    ? d === "real"
                      ? "rgba(53,194,129,0.16)"
                      : "var(--color-surface-2)"
                    : "transparent",
                  color: on
                    ? d === "real"
                      ? "var(--color-clear)"
                      : "var(--color-ink)"
                    : "var(--color-ink-muted)",
                }}
              >
                {d === "real" ? t("chip.real") : t("chip.synthetic")}
              </button>
            );
          })}
        </div>
        {health && (
          <span className="mono hidden text-[10px] sm:inline" style={{ color: "var(--color-ink-muted)" }}>
            {health.model}
          </span>
        )}
        <button
          onClick={() => setLang(lang === "en" ? "ar" : "en")}
          className="rounded-md border px-2.5 py-1 text-xs transition-colors hover:border-[var(--color-ink-muted)]"
          style={{ borderColor: "var(--color-rule)", background: "var(--color-surface)", fontFamily: lang === "en" ? "var(--font-arabic)" : "var(--font-mono)" }}
        >
          {t("lang.toggle")}
        </button>
      </div>
    </header>
  );
}
