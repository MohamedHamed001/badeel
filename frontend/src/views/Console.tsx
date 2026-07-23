import type { RegistryOptions, SubstitutionAnswer } from "../types";
import { verdict, toneColor } from "../verdict";
import { QueryBar } from "../components/QueryBar";
import { TierRail } from "../components/TierRail";
import { SubstituteCard } from "../components/SubstituteCard";
import { SafetyPanel } from "../components/SafetyPanel";
import { BlockedList } from "../components/BlockedList";

interface Props {
  options: RegistryOptions | null;
  query: { text: string; patient_flags: string[]; concurrent_meds: string[] };
  onChange: (v: Props["query"]) => void;
  onSubmit: () => void;
  answer: SubstitutionAnswer | null;
  loading: boolean;
  error: string | null;
}

export function Console(props: Props) {
  const { answer, loading, error } = props;
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

      {answer && <Result answer={answer} />}
    </div>
  );
}

function Result({ answer }: { answer: SubstitutionAnswer }) {
  const v = verdict(answer);
  const color = toneColor[v.tone];

  return (
    <div className="mt-8 border-t pt-8" style={{ borderColor: "var(--color-rule)" }}>
      {/* Verdict line — the largest element on screen. */}
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <h2
          className="text-3xl font-semibold tracking-tight sm:text-4xl"
          style={{ color }}
        >
          {v.text}
        </h2>
        {answer.query.resolved_brand && (
          <span className="mono text-sm" style={{ color: "var(--color-ink-muted)" }}>
            {answer.query.resolved_brand} · {answer.query.ingredient}
            {answer.query.strength ? ` · ${answer.query.strength}` : ""}
          </span>
        )}
      </div>

      {answer.escalation_reason && (
        <p className="mt-2 max-w-3xl text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
          {answer.escalation_reason}
        </p>
      )}

      <div className="mt-8 grid gap-8 lg:grid-cols-[190px_1fr_240px]">
        <TierRail answer={answer} />

        <div className="space-y-3">
          {answer.substitutes.length > 0 ? (
            answer.substitutes.map((s, i) => (
              <SubstituteCard key={i} sub={s} rank={i + 1} />
            ))
          ) : (
            <div className="label">No substitute offered</div>
          )}
          <BlockedList blocked={answer.blocked_candidates} />
        </div>

        <SafetyPanel flags={answer.safety_flags} />
      </div>

      <div className="mono mt-8 flex flex-wrap gap-x-4 gap-y-1 text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
        <span>model: {answer.model_used}</span>
        <span>guard trips: {answer.guard_trips}</span>
        <span>latency: {answer.latency_ms} ms</span>
        <span>resolution: {answer.query.resolution_score.toFixed(0)}</span>
      </div>
    </div>
  );
}
