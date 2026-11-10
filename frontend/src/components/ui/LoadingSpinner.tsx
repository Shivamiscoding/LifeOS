import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  fullPage?: boolean;
}

const sizeMap = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' };

export function LoadingSpinner({ size = 'md', className = '', fullPage }: LoadingSpinnerProps) {
  const spinner = <Loader2 className={`animate-spin text-accent ${sizeMap[size]} ${className}`} />;
  if (fullPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-surface/80 z-50">
        {spinner}
      </div>
    );
  }
  return spinner;
}
