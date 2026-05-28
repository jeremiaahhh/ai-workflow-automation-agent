export type WorkflowStatus =
  | "draft"
  | "planned"
  | "approved"
  | "running"
  | "completed"
  | "failed"
  | "rejected";

export type ExecutionStepStatus =
  | "pending"
  | "running"
  | "succeeded"
  | "failed"
  | "skipped";

export interface ExecutionStep {
  id: string;
  position: number;
  tool_name: string;
  description: string;
  arguments: Record<string, unknown>;
  status: ExecutionStepStatus;
  output: Record<string, unknown> | null;
  error_message: string | null;
  duration_ms: number | null;
  started_at: string | null;
  finished_at: string | null;
}

export interface WorkflowSummary {
  id: string;
  title: string;
  goal: string;
  status: WorkflowStatus;
  used_mock: boolean;
  created_at: string;
  updated_at: string;
  step_count: number;
  completed_steps: number;
}

export interface WorkflowDetail extends WorkflowSummary {
  context: string | null;
  error_message: string | null;
  report_markdown: string | null;
  steps: ExecutionStep[];
}

export interface PlannedStep {
  position: number;
  tool_name: string;
  description: string;
  arguments: Record<string, unknown>;
}

export interface AgentPlan {
  workflow_id: string;
  rationale: string;
  steps: PlannedStep[];
  used_mock: boolean;
}

export interface WorkflowStats {
  total: number;
  running: number;
  completed: number;
  failed: number;
  awaiting_approval: number;
  avg_step_count: number;
}

export interface ToolDefinition {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
}

export interface ReportResponse {
  workflow_id: string;
  title: string;
  status: WorkflowStatus;
  markdown: string;
  generated_at: string;
}

export interface HealthResponse {
  status: string;
  app: string;
  mock_mode: boolean;
  registered_tools: string[];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
