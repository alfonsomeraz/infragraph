import type {
  BlastRadiusOut,
  FindingListOut,
  GraphOut,
  IngestionRunOut,
  ResourceListOut,
  ResourceOut,
} from "./types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

// Resources

export interface ListResourcesParams {
  resource_type?: string;
  provider?: string;
  source?: string;
  limit?: number;
  offset?: number;
}

export function listResources(params: ListResourcesParams = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined) qs.set(k, String(v));
  }
  const query = qs.toString();
  return request<ResourceListOut>(`/resources${query ? `?${query}` : ""}`);
}

export function getResource(id: string) {
  return request<ResourceOut>(`/resources/${id}`);
}

// Graph

export function getGraph(resourceId: string) {
  return request<GraphOut>(`/graph/${resourceId}`);
}

export function getBlastRadius(resourceId: string, depth: number = 3) {
  return request<BlastRadiusOut>(`/graph/${resourceId}/blast-radius?depth=${depth}`);
}

// Findings

export interface ListFindingsParams {
  finding_type?: string;
  severity?: string;
  resource_id?: string;
  limit?: number;
  offset?: number;
}

export function listFindings(params: ListFindingsParams = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined) qs.set(k, String(v));
  }
  const query = qs.toString();
  return request<FindingListOut>(`/findings${query ? `?${query}` : ""}`);
}

export function scanFindings() {
  return request<FindingListOut>("/findings/scan", { method: "POST" });
}

// Ingestion

export async function uploadFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  return request<IngestionRunOut>("/ingest/upload", {
    method: "POST",
    body: form,
  });
}

export function getIngestionRun(runId: string) {
  return request<IngestionRunOut>(`/ingest/${runId}`);
}

// SWR fetcher
export const fetcher = <T>(url: string) => request<T>(url);
