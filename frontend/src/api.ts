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
