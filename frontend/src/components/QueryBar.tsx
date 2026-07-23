import type { RegistryOptions } from "../types";
import { useLang } from "../LangContext";
import { FLAG_AR } from "../i18n";

interface Props {
  options: RegistryOptions | null;
  loading: boolean;
  value: { text: string; patient_flags: string[]; concurrent_meds: string[] };
  onChange: (v: Props["value"]) => void;
  onSubmit: () => void;
}

export function QueryBar({ options, loading, value, onChange, onSubmit }: Props) {
  const { t, lang } = useLang();
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          dir="auto"
          value={value.text}
          onChange={(e) => onChange({ ...value, text: e.target.value })}
          onKeyDown={(e) => e.key === "Enter" && !loading && value.text && onSubmit()}
          placeholder={t("query.placeholder")}
          className="min-w-0 flex-1 border bg-white px-3 py-2.5 text-sm outline-none focus:border-[var(--color-ink)]"
          style={{ borderColor: "var(--color-rule)", fontFamily: "var(--font-arabic)" }}
        />
        <button
          onClick={onSubmit}
          disabled={loading || !value.text}
          className="px-5 py-2.5 text-sm font-medium disabled:opacity-40"
          style={{ background: "var(--color-ink)", color: "var(--color-paper)" }}
        >
          {loading ? "…" : t("query.analyze")}
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <ChipGroup
          label={t("query.flags")}
          all={options?.patient_flags ?? []}
          selected={value.patient_flags}
          display={(f) => (lang === "ar" ? FLAG_AR[f] ?? f : f)}
          onToggle={(f) =>
            onChange({ ...value, patient_flags: toggle(value.patient_flags, f) })
          }
        />
        <ChipGroup
          label={t("query.meds")}
          all={options?.ingredients ?? []}
          selected={value.concurrent_meds}
          display={(m) => m}
          onToggle={(m) =>
            onChange({ ...value, concurrent_meds: toggle(value.concurrent_meds, m) })
          }
          scroll
        />
      </div>
    </div>
  );
}

function ChipGroup({
  label,
  all,
  selected,
  onToggle,
  display,
  scroll,
}: {
  label: string;
  all: string[];
  selected: string[];
  onToggle: (v: string) => void;
  display: (v: string) => string;
  scroll?: boolean;
}) {
  return (
    <div>
      <div className="label mb-1.5">{label}</div>
      <div className={`flex flex-wrap gap-1.5 ${scroll ? "max-h-24 overflow-y-auto" : ""}`}>
        {all.map((item) => {
          const on = selected.includes(item);
          return (
            <button
              key={item}
              onClick={() => onToggle(item)}
              className="border px-2 py-1 text-xs"
              style={{
                borderColor: on ? "var(--color-ink)" : "var(--color-rule)",
                background: on ? "var(--color-ink)" : "transparent",
                color: on ? "var(--color-paper)" : "var(--color-ink-muted)",
              }}
            >
              {display(item)}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function toggle(list: string[], v: string): string[] {
  return list.includes(v) ? list.filter((x) => x !== v) : [...list, v];
}
