import { CheckCircle2, Clock, XCircle, Loader2, ChevronDown, ChevronRight, Wrench } from 'lucide-react';
import type { PlanStep, ToolCall } from '../../types';
import { useState } from 'react';

const stepIcons: Record<string, React.ReactNode> = {
  success: <CheckCircle2 className="w-4 h-4 text-success" />,
  failed: <XCircle className="w-4 h-4 text-error" />,
  running: <Loader2 className="w-4 h-4 text-accent animate-spin" />,
  pending: <Clock className="w-4 h-4 text-text-muted" />,
  skipped: <Clock className="w-4 h-4 text-text-muted opacity-50" />,
};

function ToolCallItem({ call }: { call: ToolCall }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-surface-border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-surface-hover text-left"
      >
        <Wrench className="w-3.5 h-3.5 text-accent" />
        <span className="text-xs font-mono text-text-primary flex-1">{call.name}</span>
        {call.status === 'running' && <Loader2 className="w-3 h-3 animate-spin text-accent" />}
        {call.status === 'success' && <CheckCircle2 className="w-3 h-3 text-success" />}
        {call.status === 'failed' && <XCircle className="w-3 h-3 text-error" />}
        {open ? <ChevronDown className="w-3 h-3 text-text-muted" /> : <ChevronRight className="w-3 h-3 text-text-muted" />}
      </button>
      {open && (
        <div className="border-t border-surface-border bg-surface/40 px-3 py-2 space-y-2">
          <div>
            <p className="text-xs text-text-muted mb-1">Input</p>
            <pre className="text-xs text-text-secondary overflow-x-auto font-mono bg-surface-card rounded p-2 max-h-32">
              {JSON.stringify(call.input, null, 2)}
            </pre>
          </div>
          {call.output !== undefined && (
            <div>
              <p className="text-xs text-text-muted mb-1">Output</p>
              <pre className="text-xs text-text-secondary overflow-x-auto font-mono bg-surface-card rounded p-2 max-h-32">
                {typeof call.output === 'string' ? call.output : JSON.stringify(call.output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface PlanDisplayProps {
  steps: PlanStep[];
  toolCalls?: ToolCall[];
  result?: string;
}

export function PlanDisplay({ steps, toolCalls, result }: PlanDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-start gap-3 p-3 rounded-xl bg-surface/40 border border-surface-border">
            <div className="mt-0.5 shrink-0">{stepIcons[step.status] || stepIcons.pending}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs text-text-muted">Step {i + 1}</span>
                {step.toolName && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-accent/10 text-accent border border-accent/20 font-mono">
                    {step.toolName}
                  </span>
                )}
              </div>
              <p className="text-sm font-medium text-text-primary mt-0.5">{step.title}</p>
              {step.description && <p className="text-xs text-text-secondary mt-0.5">{step.description}</p>}
              {step.output && (
                <div className="mt-2 p-2 rounded-lg bg-surface-card border border-surface-border">
                  <p className="text-xs text-text-secondary font-mono">{step.output}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {toolCalls && toolCalls.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">Tool Calls</h4>
          <div className="space-y-1">
            {toolCalls.map((call) => <ToolCallItem key={call.id} call={call} />)}
          </div>
        </div>
      )}

      {result && (
        <div className="p-4 rounded-xl bg-success/5 border border-success/20">
          <p className="text-xs font-semibold text-success mb-1">Result</p>
          <p className="text-sm text-text-primary whitespace-pre-wrap">{result}</p>
        </div>
      )}
    </div>
  );
}
