import type {
  AgentPlan,
  ApiError,
  HealthResponse,
  ReportResponse,
  ToolDefinition,
  WorkflowDetail,
  WorkflowStats,
  WorkflowSummary,
} from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export class ApiRequestError extends Error {
  code: string;
  status: number;
  details?: Record<string, unknown>;

  constructor(opts: {
    message: string;
    code: string;
    status: number;
    details?: Record<string, unknown>;
  }) {
    super(opts.message);
    this.name = "ApiRequestError";
    this.code = opts.code;
    this.status = opts.status;
    this.details = opts.details;
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
    headers,
  });
  if (!response.ok) {
    let payload: ApiError | null = null;
    try {
      payload = (await response.json()) as ApiError;
    } catch {
      // body not JSON
    }
    throw new ApiRequestError({
      message: payload?.error?.message ?? response.statusText,
      code: payload?.error?.code ?? "http_error",
      status: response.status,
      details: payload?.error?.details,
    });
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  tools: () => request<ToolDefinition[]>("/tools"),
  stats: () => request<WorkflowStats>("/workflows/stats"),
  listWorkflows: () => request<WorkflowSummary[]>("/workflows"),
  getWorkflow: (id: string) => request<WorkflowDetail>(`/workflows/${id}`),
  createWorkflow: (data: {
    title: string;
    goal: string;
    context?: string;
  }) =>
    request<WorkflowDetail>("/workflows", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  planWorkflow: (id: string) =>
    request<AgentPlan>(`/workflows/${id}/plan`, { method: "POST" }),
  approveWorkflow: (id: string) =>
    request<WorkflowDetail>(`/workflows/${id}/approve`, { method: "POST" }),
  rejectWorkflow: (id: string) =>
    request<WorkflowDetail>(`/workflows/${id}/reject`, { method: "POST" }),
  executeWorkflow: (id: string) =>
    request<WorkflowDetail>(`/workflows/${id}/execute`, { method: "POST" }),
  getReport: (id: string) =>
    request<ReportResponse>(`/workflows/${id}/report`),
};
