import type { TaskPriority, TaskStatus } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'priority' | 'status' | 'default';
  priority?: TaskPriority;
  status?: TaskStatus;
  className?: string;
}

const priorityClasses: Record<TaskPriority, string> = {
  low: 'bg-priority-low/15 text-priority-low border-priority-low/30',
  medium: 'bg-priority-medium/15 text-priority-medium border-priority-medium/30',
  high: 'bg-priority-high/15 text-priority-high border-priority-high/30',
  critical: 'bg-priority-critical/15 text-priority-critical border-priority-critical/30',
};

const statusClasses: Record<TaskStatus, string> = {
  todo: 'bg-text-muted/15 text-text-secondary border-surface-border',
  in_progress: 'bg-info/15 text-info border-info/30',
  completed: 'bg-success/15 text-success border-success/30',
  cancelled: 'bg-error/10 text-error border-error/20',
};

export function Badge({ children, priority, status, className = '' }: BadgeProps) {
  let cls = 'bg-accent/15 text-accent border-accent/30';
  if (priority) cls = priorityClasses[priority];
  else if (status) cls = statusClasses[status];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${cls} ${className}`}>
      {children}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: TaskPriority }) {
  const labels: Record<TaskPriority, string> = { low: 'Low', medium: 'Medium', high: 'High', critical: 'Critical' };
  return <Badge priority={priority}>{labels[priority]}</Badge>;
}

export function StatusBadge({ status }: { status: TaskStatus }) {
  const labels: Record<TaskStatus, string> = {
    todo: 'To Do',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled',
  };
  return <Badge status={status}>{labels[status]}</Badge>;
}
