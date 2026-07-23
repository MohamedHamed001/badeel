import type { SubstitutionAnswer, Tier, TierStat } from "../types";
import { toneColor } from "../verdict";
import { useLang } from "../LangContext";
import { tierLabel } from "../i18n";

// The signature element (spec section 10). A vertical rail with four stops.
// Each stop shows how many candidates were generated and how many survived the
// safety filter; blocked tiers are struck through with the blocking reason in
// small caps. Resolves top to bottom as the answer arrives.

const TIERS: Tier[] = ["generic", "class", "therapeutic", "none"];

export function TierRail({ answer }: { answer: SubstitutionAnswer }) {
  const { t, lang } = useLang();
  const byTier = new Map<Tier, TierStat>(
    answer.tier_summary.map((s) => [s.tier, s]),
  );
  const winning = answer.tier;

  return (
    <div className="select-none">
      <div className="label mb-3">{t("rail.title")}</div>
      <ol className="relative">
        {TIERS.map((tier, i) => {
          const stat = byTier.get(tier);
          const isNone = tier === "none";
          const active = winning === tier;
          const generated = stat?.generated ?? 0;
          const survived = stat?.survived ?? 0;
          const blocked = !isNone && generated > 0 && survived === 0;
          const reason = stat?.blocked_reason;

          const tone = active
            ? isNone
              ? "stop"
              : answer.substitutes.some((s) => s.counselling_flags.length)
                ? "caution"
                : "clear"
            : "neutral";
          const color = active ? toneColor[tone] : "var(--color-ink-muted)";

          return (
            <li
              key={tier}
              className="rail-stop relative flex gap-3 pb-5 ps-6"
              style={{ animationDelay: `${i * 90}ms` }}
            >
              {/* connector line */}
              {i < TIERS.length - 1 && (
                <span
                  className="absolute start-[5px] top-3 h-full w-px"
                  style={{ background: "var(--color-rule)" }}
                />
              )}
              {/* stop dot */}
              <span
                className="absolute start-0 top-1.5 h-[11px] w-[11px] rounded-full border-2"
                style={{
                  borderColor: active ? color : "var(--color-rule)",
                  background: active ? color : "var(--color-paper)",
                }}
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-2">
                  <span
                    className={`text-sm ${blocked ? "line-through" : ""}`}
                    style={{
                      color: active ? color : "var(--color-ink)",
                      fontWeight: active ? 600 : 400,
                      textDecorationColor: "var(--color-ink-muted)",
                    }}
                  >
                    {tierLabel(lang, tier)}
                  </span>
                  {!isNone && (
                    <span className="mono text-[11px]" style={{ color: "var(--color-ink-muted)" }}>
                      {survived}/{generated}
                    </span>
                  )}
                </div>
                {blocked && reason && (
                  <div
                    className="label mt-0.5 normal-case"
                    style={{ letterSpacing: "0.02em" }}
                  >
                    {reason}
                  </div>
                )}
                {active && isNone && answer.escalation_reason && (
                  <div className="mt-0.5 text-xs" style={{ color }}>
                    escalated
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
