import type { SubstitutionAnswer } from "./types";

export type Tone = "clear" | "caution" | "stop" | "neutral";

export interface Verdict {
  text: string;
  tone: Tone;
}

// The verdict line: the largest element on screen, states the outcome plainly.
export function verdict(a: SubstitutionAnswer): Verdict {
  if (a.query.unresolved) return { text: "Not in registry", tone: "stop" };
  if (a.escalate) return { text: "Do not substitute", tone: "stop" };
  const hasCounselling = a.substitutes.some(
    (s) => s.counselling_flags.length > 0,
  );
  return hasCounselling
    ? { text: "Permitted with counselling", tone: "caution" }
    : { text: "Substitution permitted", tone: "clear" };
}

export const toneColor: Record<Tone, string> = {
  clear: "var(--color-clear)",
  caution: "var(--color-caution)",
  stop: "var(--color-stop)",
  neutral: "var(--color-ink-muted)",
};
