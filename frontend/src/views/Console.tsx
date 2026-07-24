import type { ReactNode } from "react";
import type { RegistryOptions, SubstitutionAnswer } from "../types";
import { verdict, toneColor, toneTint, toneGlyph } from "../verdict";
import { useLang } from "../LangContext";
import { QueryBar } from "../components/QueryBar";
import { TierRail } from "../components/TierRail";
import { SubstituteCard } from "../components/SubstituteCard";
import { SafetyPanel } from "../components/SafetyPanel";
import { BlockedList } from "../components/BlockedList";
import { AuditTrail } from "../components/AuditTrail";

type Query = { text: string; patient_flags: string[]; concurrent_meds: string[] };
type Example = { en: string; ar: string; q: Query };

interface Props {
  options: RegistryOptions | null;
  dataset: string;
  query: Query;
  onChange: (v: Query) => void;
  onSubmit: () => void;
  onExample: (q: Query) => void;
  answer: SubstitutionAnswer | null;
  loading: boolean;
  error: string | null;
}

const EXAMPLES: Record<string, Example[]> = {
  real: [
    { en: "Concor 5 short, patient has asthma", ar: "كونكور ٥ ناقص والمريض عنده ربو", q: { text: "Concor 5 mg is short and the patient has asthma", patient_flags: ["bronchial asthma"], concurrent_meds: [] } },
    { en: "Risek out, patient on Plavix", ar: "ريزك ناقص والمريض بياخد بلافيكس", q: { text: "Risek is out and the patient takes Plavix", patient_flags: [], concurrent_meds: ["Clopidogrel"] } },
    { en: "Marevan 5 mg is short", ar: "ماريفان ٥ مجم ناقص", q: { text: "Marevan 5 mg is short", patient_flags: [], concurrent_meds: [] } },
    { en: "Lipitor 20 out of stock", ar: "ليبيتور ٢٠ مش متوفر", q: { text: "Lipitor 20 mg is out of stock", patient_flags: [], concurrent_meds: [] } },
  ],
  synthetic: [
    { en: "Cardex 10, patient has asthma", ar: "كاردكس ١٠ والمريض عنده ربو", q: { text: "Cardex 10 mg is short and the patient has asthma", patient_flags: ["bronchial asthma"], concurrent_meds: [] } },
    { en: "Gastrolux out, on Clopidex", ar: "جاسترولكس ناقص وبياخد كلوبيدكس", q: { text: "Gastrolux is out and the patient takes Clopidex", patient_flags: [], concurrent_meds: ["Clopidogrex"] } },
    { en: "Coagulex 5 mg is short", ar: "كواجولكس ٥ مجم ناقص", q: { text: "Coagulex 5 mg is short", patient_flags: [], concurrent_meds: [] } },
    { en: "Atorex 20 out of stock", ar: "أتوركس ٢٠ مش متوفر", q: { text: "Atorex 20 mg is out of stock", patient_flags: [], concurrent_meds: [] } },
  ],
};

export function Console(props: Props) {
  const { answer, loading, error } = props;
  const examples = EXAMPLES[props.dataset] ?? EXAMPLES.synthetic;

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="panel p-5">
        <QueryBar
          options={props.options}
          loading={loading}
          value={props.query}
          onChange={props.onChange}
          onSubmit={props.onSubmit}
        />
      </div>

      {error && (
        <p className="mt-6 text-sm" style={{ color: "var(--color-stop)" }}>
          {error}
        </p>
      )}

      {loading && <Loader />}

      {!loading && !answer && !error && (
        <EmptyState examples={examples} onExample={props.onExample} loading={loading} />
      )}

      {!loading && answer && <Result answer={answer} onExample={props.onExample} />}
    </div>
  );
}

function Loader() {
  const { t } = useLang();
  return (
    <div className="rise mt-6 flex flex-col items-center justify-center gap-4 rounded-xl border py-20" style={{ borderColor: "var(--color-rule)" }}>
      <span
        className="h-8 w-8 animate-spin rounded-full border-2 border-transparent"
        style={{ borderTopColor: "var(--color-clear)", borderRightColor: "var(--color-clear)" }}
      />
      <span className="label">{t("loading.analyzing")}</span>
    </div>
  );
}

function EmptyState({
  examples,
  onExample,
  loading,
}: {
  examples: Example[];
  onExample: (q: Query) => void;
  loading: boolean;
}) {
  const { t, lang } = useLang();
  return (
    <div className="mt-6 rounded-xl border border-dashed p-10 text-center" style={{ borderColor: "var(--color-rule)" }}>
      <p className="text-sm" style={{ color: "var(--color-ink-muted)" }}>
        {t("empty.hint")}
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {examples.map((ex) => (
          <button
            key={ex.en}
            disabled={loading}
            onClick={() => onExample(ex.q)}
            className="rounded-md border px-3 py-1.5 text-xs transition-colors hover:border-[var(--color-ink-muted)] disabled:opacity-40"
            style={{ borderColor: "var(--color-rule)", background: "var(--color-surface)", color: "var(--color-ink)" }}
          >
            {lang === "ar" ? ex.ar : ex.en}
          </button>
        ))}
      </div>
    </div>
  );
}

function Result({
  answer,
  onExample,
}: {
  answer: SubstitutionAnswer;
  onExample: (q: Query) => void;
}) {
  const { t } = useLang();
  const v = verdict(answer);
  const color = toneColor[v.tone];
  const q = answer.query;
  const c = answer.comprehension;
  const notShortage = c?.intent === "not_a_shortage";
  const understood = c ? [c.drug, ...c.flags, ...c.meds].filter(Boolean) : [];

  return (
    <div className="rise mt-6 space-y-5">
      {/* Verdict banner — the largest element, signal-washed, unmistakable. */}
      <div
        className="relative overflow-hidden rounded-xl border p-6"
        style={{ borderColor: "var(--color-rule)", background: toneTint[v.tone] }}
      >
        <span className="absolute inset-y-0 start-0 w-1.5" style={{ background: color }} />
        <div className="ps-3">
          <div className="flex items-center gap-3">
            <span
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-base font-bold"
              style={{ background: color, color: "var(--color-bg)" }}
            >
              {toneGlyph[v.tone]}
            </span>
            <h2 className="text-3xl font-bold leading-none tracking-tight sm:text-[2.4rem]" style={{ color }}>
              {t(v.key)}
            </h2>
          </div>

          {/* What the LLM read from the free text (Python re-validated it). */}
          {understood.length > 0 && (
            <p className="mono mt-2 text-xs" style={{ color: "var(--color-ink-muted)" }}>
              {t("comprehension.understood")}: {understood.join(" · ")}
            </p>
          )}

          {/* Interpretation — what is being substituted vs. patient context.
              Suppressed for a "not a shortage" reading: nothing is substituted. */}
          {q.resolved_brand && !notShortage && (
            <div className="mt-5 flex flex-wrap items-stretch gap-x-8 gap-y-3">
              <Interpret label={t("intp.substituting")} accent={color}>
                <span className="font-semibold">{q.resolved_brand}</span>
                <span className="mono ms-2 text-xs" style={{ color: "var(--color-ink-muted)" }}>
                  {q.ingredient}
                  {q.strength ? ` · ${q.strength}` : ""}
                  {q.form ? ` · ${q.form}` : ""}
                </span>
              </Interpret>

              {q.concurrent_meds.length > 0 && (
                <Interpret label={t("intp.alsoOn")}>
                  {q.concurrent_meds.join(", ")}
                </Interpret>
              )}
              {q.patient_flags.length > 0 && (
                <Interpret label={t("intp.flags")}>
                  {q.patient_flags.join(", ")}
                </Interpret>
              )}
            </div>
          )}

          {answer.escalation_reason && (
            <p className="mt-4 max-w-3xl text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
              {answer.escalation_reason}
            </p>
          )}

          {/* Deterministic "did you mean?" — the fuzzy resolver's near-misses,
              real registered brands only. Clicking one re-runs with the patient
              context preserved. The LLM plays no part in this. */}
          {q.unresolved && q.suggestions.length > 0 && (
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="label" style={{ color: "var(--color-ink-muted)" }}>
                {t("query.didyoumean")}
              </span>
              {q.suggestions.map((s) => (
                <button
                  key={s.brand}
                  onClick={() =>
                    onExample({
                      text: s.brand,
                      patient_flags: q.patient_flags,
                      concurrent_meds: q.concurrent_meds,
                    })
                  }
                  className="rounded-md border px-3 py-1.5 text-xs transition-colors hover:border-[var(--color-ink-muted)]"
                  style={{ borderColor: "var(--color-rule)", background: "var(--color-surface)", color: "var(--color-ink)" }}
                >
                  <span className="font-semibold">{s.brand}</span>
                  <span className="mono ms-1.5" style={{ color: "var(--color-ink-muted)" }}>
                    {s.ingredient}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Working area. */}
      <div className="grid gap-5 lg:grid-cols-[210px_1fr_250px]">
        <div className="panel p-5">
          <TierRail answer={answer} />
        </div>

        <div className="space-y-4">
          {answer.substitutes.length > 0 ? (
            <>
              <SubstituteCard sub={answer.substitutes[0]} rank={1} />
              {answer.substitutes.length > 1 && (
                <div className="space-y-2">
                  <div className="label pt-1">{t("result.alternatives")}</div>
                  {answer.substitutes.slice(1).map((s, i) => (
                    <SubstituteCard key={i + 1} sub={s} rank={i + 2} compact />
                  ))}
                </div>
              )}
            </>
          ) : (
            <div
              className="panel flex items-center justify-center py-12 text-sm"
              style={{ color: "var(--color-ink-muted)" }}
            >
              {t("result.nosub")}
            </div>
          )}
          <BlockedList blocked={answer.blocked_candidates} />
          <AuditTrail trace={answer.trace} />
        </div>

        {answer.safety_flags.length > 0 ? (
          <div className="panel p-5">
            <SafetyPanel flags={answer.safety_flags} />
          </div>
        ) : (
          <div />
        )}
      </div>

      <div className="mono flex flex-wrap gap-x-4 gap-y-1 text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
        <span>{t("meta.model")}: {answer.model_used}</span>
        <span>{t("meta.trips")}: {answer.guard_trips}</span>
        <span>{t("meta.latency")}: {answer.latency_ms} ms</span>
        <span>{t("meta.resolution")}: {answer.query.resolution_score.toFixed(0)}</span>
      </div>
    </div>
  );
}

function Interpret({
  label,
  accent,
  children,
}: {
  label: string;
  accent?: string;
  children: ReactNode;
}) {
  return (
    <div
      className="border-s-2 ps-3"
      style={{ borderColor: accent ?? "var(--color-rule)" }}
    >
      <div className="label mb-0.5">{label}</div>
      <div className="text-sm" style={{ color: "var(--color-ink)" }}>{children}</div>
    </div>
  );
}
