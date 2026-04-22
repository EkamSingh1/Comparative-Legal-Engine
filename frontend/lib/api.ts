import type { AnalysisResponse, HealthResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function readJson<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail ?? `Request failed with status ${response.status}`;
    throw new Error(detail);
  }
  return body as T;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`, {
    headers: { Accept: "application/json" },
    cache: "no-store"
  });
  return readJson<HealthResponse>(response);
}

export async function analyzeScenario(scenario: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ scenario })
  });
  return readJson<AnalysisResponse>(response);
}
