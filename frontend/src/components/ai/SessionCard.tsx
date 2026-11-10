import { format } from 'date-fns';
import { CheckCircle2, XCircle, Loader2, Clock } from 'lucide-react';
import type { AISession } from '../../types';

const statusIcons: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="w-3.5 h-3.5 text-success" />,
  failed: <XCircle className="w-3.5 h-3.5 text-error" />,
  running: <Loader2 className="w-3.5 h-3.5 text-accent animate-spin" />,
  pending: <Clock className="w-3.5 h-3.5 text-text-muted" />,
};

interface SessionCardProps {
  session: AISession;
  isActive?: boolean;
  onClick: () => void;
}

export function SessionCard({ session, isActive, onClick }: SessionCardProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-3 rounded-xl border transition-all duration-150 ${
        isActive
          ? 'bg-accent/10 border-accent/40 text-text-primary'
          : 'bg-surface-card border-surface-border hover:border-accent/30 hover:bg-surface-hover text-text-secondary'
      }`}
    >
      <div className="flex items-start gap-2">
        <span className="mt-0.5 shrink-0">{statusIcons[session.status]}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium line-clamp-2 text-text-primary">{session.command}</p>
          <p className="text-xs text-text-muted mt-1">{format(new Date(session.createdAt), 'MMM d, h:mm a')}</p>
        </div>
      </div>
    </button>
  );
}
