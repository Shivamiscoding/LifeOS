import { ToastItem } from './Toast';
import { useNotification } from '../../hooks/useNotification';

export function ToastContainer() {
  const { toasts, dismiss } = useNotification();
  if (!toasts.length) return null;
  return (
    <div className="fixed bottom-6 right-6 z-[200] flex flex-col gap-2">
      {toasts.map((t) => <ToastItem key={t.id} toast={t} onDismiss={dismiss} />)}
    </div>
  );
}
