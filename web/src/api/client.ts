import type { CaseRequest, CaseResponse, Clue, WorldMap } from "../types/api";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export function pictureUrl(imageUrl: string | null | undefined): string | null {
  if (!imageUrl) return null;
  return `${API_URL}/api/image?url=${encodeURIComponent(imageUrl)}`;
}

async function readDetail(response: Response): Promise<string> {
  try {
    const payload: unknown = await response.json();
    if (payload && typeof payload === "object" && "detail" in payload) {
      const detail = (payload as { detail: unknown }).detail;
      if (typeof detail === "string" && detail.trim()) return detail;
    }
  } catch {
    /* The body was not JSON. */
  }
  if (response.status === 503) return "NASA POWER has no climate for this pin.";
  return "The farm service could not answer.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) throw new ApiError(await readDetail(response), response.status);
  return response.json() as Promise<T>;
}

function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function fetchWorldMap(): Promise<WorldMap> {
  return request<WorldMap>("/api/world-map");
}

export function fetchClues(farm: CaseRequest): Promise<Clue[]> {
  return post<{ clues: Clue[] }>("/api/clues", farm).then((body) => body.clues);
}

export function createCase(farm: CaseRequest): Promise<CaseResponse> {
  return post<CaseResponse>("/api/case", farm);
}

export function askAssistant(caseResult: CaseResponse, question: string): Promise<string> {
  return post<{ answer: string }>("/api/assistant", { case: caseResult, question }).then(
    (body) => body.answer,
  );
}
