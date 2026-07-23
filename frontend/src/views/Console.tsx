import type { RegistryOptions, SubstitutionAnswer } from "../types";
import { verdict, toneColor } from "../verdict";
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
      <QueryBar
        options={props.options}
        loading={loading}
        value={props.query}
        onChange={props.onChange}
        onSubmit={props.onSubmit}
      />

      {error && (
        <p className="mt-6 text-sm" style={{ color: "var(--color-stop)" }}>
          {error}
        </p>
      )}

      {!answer && !error && (
        <EmptyState examples={examples} onExample={props.onExample} loading={loading} />
      )}

      {answer && <Result answer={answer} />}
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
    <div
      className="mt-10 border border-dashed p-8 text-center"
      style={{ borderColor: "var(--color-rule)" }}
    >
      <p className="text-sm" style={{ color: "var(--color-ink-muted)" }}>
        {t("empty.hint")}
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {examples.map((ex) => (
          <button
            key={ex.en}
            disabled={loading}
            onClick={() => onExample(ex.q)}
            className="border px-3 py-1.5 text-xs transition-colors hover:border-[var(--color-ink)] disabled:opacity-40"
            style={{ borderColor: "var(--color-rule)", color: "var(--color-ink)" }}
          >
            {lang === "ar" ? ex.ar : ex.en}
          </button>
        ))}
      </div>
    </div>
  );
}

function Result({ answer }: { answer: SubstitutionAnswer }) {
  const { t } = useLang();
  const v = verdict(answer);
  const color = toneColor[v.tone];
  const q = answer.query;

  return (
    <div
      className="rail-stop mt-8 border-t pt-8"
      style={{ borderColor: "var(--color-rule)" }}
    >
      {/* Verdict — the largest element, with a signal accent bar. */}
      <div className="flex gap-4">
        <span
          className="mt-1 w-1 shrink-0 self-stretch rounded-full"
          style={{ background: color }}
        />
        <div className="min-w-0">
          <h2
            className="text-3xl font-semibold leading-none tracking-tight sm:text-[2.6rem]"
            style={{ color }}
          >
            {t(v.key)}
          </h2>
          {q.resolved_brand && (
            <div className="mono mt-2 text-sm" style={{ color: "var(--color-ink-muted)" }}>
              {q.resolved_brand} · {q.ingredient}
              {q.strength ? ` · ${q.strength}` : ""}
              {q.form ? ` · ${q.form}` : ""}
            </div>
          )}
          {answer.escalation_reason && (
            <p className="mt-3 max-w-3xl text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
              {answer.escalation_reason}
            </p>
          )}
        </div>
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-[190px_1fr_240px]">
        <TierRail answer={answer} />

        <div className="space-y-3">
          {answer.substitutes.length > 0 ? (
            answer.substitutes.map((s, i) => (
              <SubstituteCard key={i} sub={s} rank={i + 1} />
            ))
          ) : (
            <div
              className="flex items-center justify-center border border-dashed py-10 text-sm"
              style={{ borderColor: "var(--color-rule)", color: "var(--color-ink-muted)" }}
            >
              {t("result.nosub")}
            </div>
          )}
          <BlockedList blocked={answer.blocked_candidates} />
        </div>

        <SafetyPanel flags={answer.safety_flags} />
      </div>

      <AuditTrail trace={answer.trace} />

      <div className="mono mt-6 flex flex-wrap gap-x-4 gap-y-1 text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
        <span>{t("meta.model")}: {answer.model_used}</span>
        <span>{t("meta.trips")}: {answer.guard_trips}</span>
        <span>{t("meta.latency")}: {answer.latency_ms} ms</span>
        <span>{t("meta.resolution")}: {answer.query.resolution_score.toFixed(0)}</span>
      </div>
    </div>
  );
}
