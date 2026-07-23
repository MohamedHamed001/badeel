import type { SubstitutionAnswer } from "./types";
import type { StringKey } from "./i18n";

export type Tone = "clear" | "caution" | "stop" | "neutral";

export interface Verdict {
  key: StringKey;
  tone: Tone;
}

// The verdict line: the largest element on screen, states the outcome plainly.
export function verdict(a: SubstitutionAnswer): Verdict {
  if (a.query.unresolved) return { key: "verdict.unresolved", tone: "stop" };
  if (a.escalate) return { key: "verdict.stop", tone: "stop" };
  const hasCounselling = a.substitutes.some((s) => s.counselling_flags.length > 0);
  return hasCounselling
    ? { key: "verdict.caution", tone: "caution" }
    : { key: "verdict.clear", tone: "clear" };
}

export const toneColor: Record<Tone, string> = {
  clear: "var(--color-clear)",
  caution: "var(--color-caution)",
  stop: "var(--color-stop)",
  neutral: "var(--color-ink-muted)",
};

// Faint signal-colour wash for the verdict banner background on dark.
export const toneTint: Record<Tone, string> = {
  clear: "rgba(53, 194, 129, 0.10)",
  caution: "rgba(234, 161, 58, 0.10)",
  stop: "rgba(242, 88, 77, 0.10)",
  neutral: "rgba(138, 146, 158, 0.08)",
};

export const toneGlyph: Record<Tone, string> = {
  clear: "✓",
  caution: "!",
  stop: "✕",
  neutral: "•",
};
