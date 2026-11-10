import React from 'react';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className = '', ...props }, ref) => (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-text-secondary">
          {label}
          {props.required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      <select
        ref={ref}
        {...props}
        className={`w-full rounded-lg border bg-surface-card px-3 py-2 text-sm text-text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-accent/40 ${
          error ? 'border-error' : 'border-surface-border hover:border-text-muted'
        } ${className}`}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      {error && <span className="text-xs text-error">{error}</span>}
    </div>
  )
);
Select.displayName = 'Select';
