import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function Card({ children, className = '', ...props }: CardProps) {
  return (
    <div
      {...props}
      className={`bg-surface-card border border-surface-border rounded-xl ${className}`}
    >
      {children}
    </div>
  );
}
