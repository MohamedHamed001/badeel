import type { ReactNode } from "react";
import type { Substitute } from "../types";
import { useLang } from "../LangContext";
import { tierLabel } from "../i18n";

export function SubstituteCard({
  sub,
  rank,
  streamText = "",
  narrating = false,
  compact = false,
}: {
  sub: Substitute;
  rank: number;
  streamText?: string;
  narrating?: boolean;
  compact?: boolean;
}) {
  const { lang, t } = useLang();
  const delta = sub.price_delta_pct;
  const deltaStr = `${delta > 0 ? "+" : ""}${delta.toFixed(0)}%`;
  const streaming = narrating || streamText.length > 0;
  const waiting = narrating && streamText.length === 0;

  // Secondary options (alternative brands of the same tier) render as a slim
  // row — the primary recommendation carries the rationale.
  if (compact) {
    return (
      <div
        className="flex items-center justify-between gap-3 rounded-lg border px-4 py-3"
        style={{ borderColor: "var(--color-rule)", background: "var(--color-surface)" }}
      >
        <div className="flex items-baseline gap-2.5">
          <span className="mono text-xs" style={{ color: "var(--color-ink-muted)" }}>
            {String(rank).padStart(2, "0")}
          </span>
          <span className="text-sm font-semibold">{sub.brand}</span>
          <span className="text-xs" style={{ color: "var(--color-ink-muted)" }}>
            {sub.ingredient}
          </span>
        </div>
        <div className="mono flex items-center gap-2 text-xs">
          <Chip>{sub.strength}</Chip>
          <Chip>EGP {sub.price_egp.toFixed(2)}</Chip>
          {delta !== 0 && (
            <Chip color={delta > 0 ? "var(--color-caution)" : "var(--color-clear)"}>
              {deltaStr}
            </Chip>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-baseline gap-2.5">
          <span className="mono text-xs" style={{ color: "var(--color-ink-muted)" }}>
            {String(rank).padStart(2, "0")}
          </span>
          <div>
            <h3 className="text-lg font-semibold leading-tight">{sub.brand}</h3>
            <span className="text-sm" style={{ color: "var(--color-ink-muted)" }}>
              {sub.ingredient}
            </span>
          </div>
        </div>
        <span
          className="label rounded-full px-2.5 py-1"
          style={{ background: "var(--color-surface-2)", color: "var(--color-ink)" }}
        >
          {tierLabel(lang, sub.tier)}
        </span>
      </div>

      <div className="mono mt-3 flex flex-wrap gap-2 text-xs">
        <Chip>{sub.strength}</Chip>
        <Chip muted>{sub.form}</Chip>
        <Chip>EGP {sub.price_egp.toFixed(2)}</Chip>
        {delta !== 0 && (
          <Chip color={delta > 0 ? "var(--color-caution)" : "var(--color-clear)"}>
            {deltaStr}
          </Chip>
        )}
      </div>

      {(streaming || sub.rationale) && (
        <p className="mt-4 text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
          {waiting ? (
            <span className="italic" style={{ color: "var(--color-ink-muted)" }}>
              {t("card.generating")}
              <span
                className="ms-1 inline-block h-3.5 w-1.5 translate-y-0.5 animate-pulse"
                style={{ background: "var(--color-clear)" }}
              />
            </span>
          ) : (
            sub.rationale
          )}
        </p>
      )}

      {sub.counselling_flags.length > 0 && (
        <ul className="mt-4 space-y-1.5 border-t pt-3" style={{ borderColor: "var(--color-rule)" }}>
          {sub.counselling_flags.map((f, i) => (
            <li key={i} className="flex gap-2 text-xs leading-relaxed" style={{ color: "var(--color-ink)" }}>
              <span style={{ color: "var(--color-caution)" }}>▸</span>
              <span>{f}</span>
            </li>
          ))}
        </ul>
      )}

      {sub.evidence.length > 0 && (
        <div className="mono mt-3 flex flex-wrap gap-x-3 gap-y-1 text-[10px]" style={{ color: "var(--color-ink-muted)" }}>
          {sub.evidence.slice(0, 4).map((c, i) => (
            <span key={i}>
              {c.leaflet} · {c.section}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function Chip({
  children,
  muted,
  color,
}: {
  children: ReactNode;
  muted?: boolean;
  color?: string;
}) {
  return (
    <span
      className="rounded px-2 py-0.5"
      style={{
        background: "var(--color-surface-2)",
        color: color ?? (muted ? "var(--color-ink-muted)" : "var(--color-ink)"),
      }}
    >
      {children}
    </span>
  );
}
