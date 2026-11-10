import { Calendar, Edit2, Trash2, CheckCircle2, Circle, FolderOpen } from 'lucide-react';
import type { Task } from '../../types';
import { PriorityBadge, StatusBadge } from '../ui/Badge';

function formatDue(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(d);
  } catch {
    return dateStr;
  }
}

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onStatusToggle: (task: Task) => void;
  compact?: boolean;
}

export function TaskCard({ task, onEdit, onDelete, onStatusToggle, compact }: TaskCardProps) {
  const isCompleted = task.status === 'completed';
  return (
    <div className={`group bg-surface-card border border-surface-border rounded-xl p-4 hover:border-accent/40 transition-all duration-200 ${compact ? '' : ''}`}>
      <div className="flex items-start gap-3">
        <button
          onClick={() => onStatusToggle(task)}
          className="mt-0.5 shrink-0 text-text-muted hover:text-accent transition-colors"
        >
          {isCompleted ? (
            <CheckCircle2 className="w-5 h-5 text-success" />
          ) : (
            <Circle className="w-5 h-5" />
          )}
        </button>
        <div className="flex-1 min-w-0">
          <p className={`text-sm font-medium truncate ${isCompleted ? 'line-through text-text-muted' : 'text-text-primary'}`}>
            {task.title}
          </p>
          {task.description && !compact && (
            <p className="text-xs text-text-secondary mt-1 line-clamp-2">{task.description}</p>
          )}
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <PriorityBadge priority={task.priority} />
            <StatusBadge status={task.status} />
            {task.project && (
              <span className="inline-flex items-center gap-1 text-xs text-text-secondary">
                <FolderOpen className="w-3 h-3" />
                {task.project.name}
              </span>
            )}
            {task.dueDate && (
              <span className="inline-flex items-center gap-1 text-xs text-text-muted">
                <Calendar className="w-3 h-3" />
                {formatDue(task.dueDate)}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
          <button onClick={() => onEdit(task)} className="p-1.5 rounded-lg text-text-muted hover:text-accent hover:bg-accent/10 transition-colors">
            <Edit2 className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => onDelete(task)} className="p-1.5 rounded-lg text-text-muted hover:text-error hover:bg-error/10 transition-colors">
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
