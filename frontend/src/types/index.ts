// ============================================================
// LifeOS – TypeScript interfaces
// ============================================================

// ─── Enums ───────────────────────────────────────────────────
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskStatus = 'todo' | 'in_progress' | 'completed' | 'cancelled';
export type AutomationTrigger = 'schedule' | 'event' | 'manual' | 'webhook';
export type AISessionStatus = 'pending' | 'running' | 'completed' | 'failed';
export type StepStatus = 'pending' | 'running' | 'success' | 'failed' | 'skipped';

// ─── Auth ─────────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  timezone?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthTokens {
  access: string;
  refresh?: string;
}

// ─── Tasks ────────────────────────────────────────────────────
export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate?: string;
  projectId?: string;
  project?: Project;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateTaskPayload {
  title: string;
  description?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  dueDate?: string;
  projectId?: string;
  tags?: string[];
}

export interface UpdateTaskPayload extends Partial<CreateTaskPayload> {
  id: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  projectId?: string;
  search?: string;
  sortBy?: 'dueDate' | 'priority' | 'createdAt' | 'title';
  sortOrder?: 'asc' | 'desc';
}

// ─── Projects ─────────────────────────────────────────────────
export interface Project {
  id: string;
  name: string;
  description?: string;
  color?: string;
  deadline?: string;
  taskCount?: number;
  completedTaskCount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  color?: string;
  deadline?: string;
}

// ─── Calendar ─────────────────────────────────────────────────
export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  allDay?: boolean;
  color?: string;
  location?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateEventPayload {
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  allDay?: boolean;
  color?: string;
  location?: string;
}

// ─── Files ────────────────────────────────────────────────────
export interface FileDocument {
  id: string;
  name: string;
  mimeType: string;
  size: number;
  url?: string;
  summary?: string;
  uploadedAt: string;
}

// ─── Automations ─────────────────────────────────────────────
export interface Automation {
  id: string;
  name: string;
  description?: string;
  trigger: AutomationTrigger;
  triggerConfig?: Record<string, unknown>;
  actions: AutomationAction[];
  isActive: boolean;
  lastRunAt?: string;
  runCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface AutomationAction {
  type: string;
  config: Record<string, unknown>;
}

export interface ExecutionLog {
  id: string;
  automationId: string;
  status: 'success' | 'failed';
  startedAt: string;
  finishedAt?: string;
  logs?: string;
  error?: string;
}

export interface CreateAutomationPayload {
  name: string;
  description?: string;
  trigger: AutomationTrigger;
  triggerConfig?: Record<string, unknown>;
  actions: AutomationAction[];
}

// ─── AI / Command Center ─────────────────────────────────────
export interface AISession {
  id: string;
  command: string;
  status: AISessionStatus;
  plan?: PlanStep[];
  result?: string;
  toolCalls?: ToolCall[];
  createdAt: string;
  updatedAt: string;
}

export interface PlanStep {
  id: string;
  title: string;
  description?: string;
  status: StepStatus;
  toolName?: string;
  output?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, unknown>;
  output?: unknown;
  status: StepStatus;
  startedAt?: string;
  finishedAt?: string;
}

export interface SendCommandPayload {
  command: string;
  sessionId?: string;
}

// ─── Insights / Dashboard ────────────────────────────────────
export interface DashboardStats {
  totalTasks: number;
  completedToday: number;
  activeProjects: number;
  pendingEvents: number;
  streak: number;
  avgCompletionRate: number;
}

export interface ProductivityDataPoint {
  date: string;
  completed: number;
  created: number;
}

export interface PriorityDistribution {
  priority: TaskPriority;
  count: number;
}

export interface DayOfWeekData {
  day: string;
  completed: number;
}

export interface ProjectCompletionRate {
  projectName: string;
  rate: number;
  total: number;
  completed: number;
}

export interface InsightsData {
  productivity: ProductivityDataPoint[];
  priorityDistribution: PriorityDistribution[];
  dayOfWeekData: DayOfWeekData[];
  projectCompletionRates: ProjectCompletionRate[];
}

// ─── Pagination ───────────────────────────────────────────────
export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}
