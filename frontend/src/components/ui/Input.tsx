import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className = '', ...props }, ref) => (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-text-secondary">
          {label}
          {props.required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      <input
        ref={ref}
        {...props}
        className={`w-full rounded-lg border bg-surface-card px-3 py-2 text-sm text-text-primary placeholder-text-muted transition-colors focus:outline-none focus:ring-2 focus:ring-accent/40 ${
          error ? 'border-error' : 'border-surface-border hover:border-text-muted'
        } ${className}`}
      />
      {error && <span className="text-xs text-error">{error}</span>}
      {hint && !error && <span className="text-xs text-text-muted">{hint}</span>}
    </div>
  )
);
Input.displayName = 'Input';
