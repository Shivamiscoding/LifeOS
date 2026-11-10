import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import type { Toast } from '../../contexts/NotificationContext';

const iconMap = {
  success: <CheckCircle2 className="w-4 h-4" />,
  error: <AlertCircle className="w-4 h-4" />,
  info: <Info className="w-4 h-4" />,
  warning: <AlertTriangle className="w-4 h-4" />,
};

const colorMap = {
  success: 'border-success/40 bg-success/10 text-success',
  error: 'border-error/40 bg-error/10 text-error',
  info: 'border-info/40 bg-info/10 text-info',
  warning: 'border-warning/40 bg-warning/10 text-warning',
};

interface ToastItemProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

export function ToastItem({ toast, onDismiss }: ToastItemProps) {
  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg backdrop-blur-sm ${colorMap[toast.type]} bg-surface-card/90 max-w-sm w-full`}>
      <span className="mt-0.5 shrink-0">{iconMap[toast.type]}</span>
      <p className="text-sm text-text-primary flex-1">{toast.message}</p>
      <button onClick={() => onDismiss(toast.id)} className="shrink-0 text-text-muted hover:text-text-primary">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
