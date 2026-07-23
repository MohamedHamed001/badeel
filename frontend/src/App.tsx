import { useEffect, useRef, useState } from "react";
import { api, substituteStream } from "./api";
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

  const [query, setQuery] = useState<Query>(EMPTY);
  const [answer, setAnswer] = useState<SubstitutionAnswer | null>(null);
  const [streamText, setStreamText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastRun = useRef<Query | null>(null);

  const dir = lang === "ar" ? "rtl" : "ltr";

  useEffect(() => {
    document.documentElement.dir = dir;
    document.documentElement.lang = lang;
  }, [dir, lang]);

  useEffect(() => {
    api.options().then(setOptions).catch(() => {});
    api.health().then(setHealth).catch(() => {});
  }, []);

  async function run(q: Query, l: Lang = lang) {
    lastRun.current = q;
    setLoading(true);
    setError(null);
    setStreamText("");
    await substituteStream(
      { ...q, lang: l },
      {
        onAnswer: (a) => {
          setAnswer(a);
          setLoading(false); // deterministic result is ready; prose streams next
        },
        onDelta: (i, text) => {
          if (i === 0) setStreamText((t) => t + text);
        },
        onDone: (i, d) => {
          setStreamText("");
          setAnswer((prev) =>
            prev
              ? {
                  ...prev,
                  guard_trips: prev.guard_trips + (d.guard_trip ? 1 : 0),
                  substitutes: prev.substitutes.map((s, idx) =>
                    idx === i
                      ? { ...s, rationale: d.rationale, evidence: (d.evidence as typeof s.evidence) ?? s.evidence }
                      : s,
                  ),
                }
              : prev,
          );
        },
        onError: (e) => {
          setError(`Request failed: ${e}`);
          setAnswer(null);
          setLoading(false);
        },
      },
    );
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
    setQuery(q);
    setView("console");
    run(q);
  }

  return (
    <LangProvider value={{ lang, dir, t: makeT(lang), setLang }}>
      <div className="flex min-h-full flex-col">
        <SyntheticBanner />
        <Header view={view} setView={setView} health={health} />

        <main className="flex-1">
          {view === "console" && (
            <Console
              options={options}
              dataset={health?.dataset ?? "synthetic"}
              query={query}
              onChange={setQuery}
              onSubmit={() => run(query)}
              onExample={(q) => {
                setQuery(q);
                run(q);
              }}
              answer={answer}
              streamText={streamText}
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
}: {
  view: View;
  setView: (v: View) => void;
  health: Health | null;
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
      style={{ borderColor: "var(--color-rule)" }}
    >
      <div className="flex items-baseline gap-6">
        <span className="text-base font-semibold tracking-tight">
          Badeel<span style={{ color: "var(--color-ink-muted)" }}> · بديل</span>
        </span>
        <nav className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              className="px-2.5 py-1 text-sm"
              style={{
                color: view === tab.id ? "var(--color-ink)" : "var(--color-ink-muted)",
                borderBottom: view === tab.id ? "2px solid var(--color-ink)" : "2px solid transparent",
                fontWeight: view === tab.id ? 600 : 400,
              }}
            >
              {t(tab.key)}
            </button>
          ))}
        </nav>
      </div>

      <div className="flex items-center gap-3">
        {health && (
          <div className="mono hidden items-center gap-2 text-[10px] sm:flex" style={{ color: "var(--color-ink-muted)" }}>
            <span
              className="rounded-sm px-1.5 py-0.5"
              style={{
                background: health.dataset === "real" ? "var(--color-clear)" : "var(--color-rule)",
                color: health.dataset === "real" ? "var(--color-paper)" : "var(--color-ink-muted)",
              }}
            >
              {health.dataset === "real" ? t("chip.real") : t("chip.synthetic")}
            </span>
            <span>{health.model}</span>
          </div>
        )}
        <button
          onClick={() => setLang(lang === "en" ? "ar" : "en")}
          className="border px-2 py-1 text-xs"
          style={{ borderColor: "var(--color-rule)", fontFamily: lang === "en" ? "var(--font-arabic)" : "var(--font-mono)" }}
        >
          {t("lang.toggle")}
        </button>
      </div>
    </header>
  );
}
