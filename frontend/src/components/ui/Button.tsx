import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantClasses: Record<string, string> = {
  primary: 'bg-accent hover:bg-accent-dark text-white border-transparent',
  secondary: 'bg-surface-card hover:bg-surface-hover text-text-primary border-surface-border',
  ghost: 'bg-transparent hover:bg-surface-hover text-text-secondary hover:text-text-primary border-transparent',
  danger: 'bg-error/10 hover:bg-error/20 text-error border-error/30',
};

const sizeClasses: Record<string, string> = {
  sm: 'px-3 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2 text-sm gap-2',
  lg: 'px-6 py-3 text-base gap-2.5',
};

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading,
  leftIcon,
  rightIcon,
  children,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center rounded-lg border font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {isLoading ? <Loader2 className="animate-spin w-4 h-4" /> : leftIcon}
      {children}
      {!isLoading && rightIcon}
    </button>
  );
}
