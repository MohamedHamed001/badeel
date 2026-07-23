// Typed client mirroring the backend routes (spec section 7).

import type {
  EvalCase,
  Health,
  RegistryOptions,
  SubstitutionAnswer,
} from "./types";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

export interface SubstituteRequest {
  text: string;
  patient_flags?: string[];
  concurrent_meds?: string[];
  lang?: "en" | "ar";
}

export interface StreamHandlers {
  onAnswer: (a: SubstitutionAnswer) => void;
  onNarrating: (i: number) => void;
  onDelta: (i: number, text: string) => void;
  onDone: (i: number, d: { rationale: string; evidence?: unknown[]; guard_trip?: boolean }) => void;
  onError: (e: string) => void;
}

// Consume the Server-Sent-Events stream: deterministic `answer` first, then
// `delta` tokens for the live-typing rationale, then `done`.
export async function substituteStream(body: SubstituteRequest, h: StreamHandlers) {
  let res: Response;
  try {
    res = await fetch("/api/substitute/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (e) {
    h.onError(String(e));
    return;
  }
  if (!res.ok || !res.body) {
    h.onError(`${res.status} ${res.statusText}`);
    return;
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let sep: number;
    while ((sep = buf.indexOf("\n\n")) >= 0) {
      const block = buf.slice(0, sep);
      buf = buf.slice(sep + 2);
      let event = "message";
      let data = "";
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      const parsed = JSON.parse(data);
      if (event === "answer") h.onAnswer(parsed as SubstitutionAnswer);
      else if (event === "narrating") h.onNarrating(parsed.i);
      else if (event === "delta") h.onDelta(parsed.i, parsed.text);
      else if (event === "done") h.onDone(parsed.i, parsed);
    }
  }
}

export const api = {
  substitute(body: SubstituteRequest): Promise<SubstitutionAnswer> {
    return fetch("/api/substitute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(json<SubstitutionAnswer>);
  },
  options(): Promise<RegistryOptions> {
    return fetch("/api/registry/options").then(json<RegistryOptions>);
  },
  evalCases(): Promise<EvalCase[]> {
    return fetch("/api/eval/cases").then(json<EvalCase[]>);
  },
  evalResults(): Promise<unknown> {
    return fetch("/api/eval/results").then((r) => r.json());
  },
  health(): Promise<Health> {
    return fetch("/api/health").then(json<Health>);
  },
};
