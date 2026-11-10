import type { Task, TaskStatus } from '../../types';
import { TaskCard } from './TaskCard';
import { EmptyState } from '../ui/EmptyState';
import { CheckSquare } from 'lucide-react';

const COLUMNS: { key: TaskStatus; label: string; color: string }[] = [
  { key: 'todo', label: 'To Do', color: 'border-t-text-muted' },
  { key: 'in_progress', label: 'In Progress', color: 'border-t-info' },
  { key: 'completed', label: 'Completed', color: 'border-t-success' },
];

interface KanbanBoardProps {
  tasks: Task[];
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onStatusToggle: (task: Task) => void;
}

export function KanbanBoard({ tasks, onEdit, onDelete, onStatusToggle }: KanbanBoardProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {COLUMNS.map((col) => {
        const colTasks = tasks.filter((t) => t.status === col.key);
        return (
          <div key={col.key} className={`bg-surface/40 rounded-xl border-t-2 ${col.color} border border-surface-border p-4`}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-text-secondary">{col.label}</h3>
              <span className="text-xs bg-surface-hover text-text-muted px-2 py-0.5 rounded-full">{colTasks.length}</span>
            </div>
            <div className="flex flex-col gap-2">
              {colTasks.length === 0 ? (
                <EmptyState
                  icon={<CheckSquare className="w-6 h-6" />}
                  title="No tasks"
                  description="Drag tasks here or create new ones"
                />
              ) : (
                colTasks.map((t) => (
                  <TaskCard key={t.id} task={t} onEdit={onEdit} onDelete={onDelete} onStatusToggle={onStatusToggle} compact />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
