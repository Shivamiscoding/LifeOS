import { useState, useRef } from 'react';
import { Send, Zap } from 'lucide-react';

const SUGGESTIONS = [
  'Plan my day based on pending tasks',
  'Create a weekly study schedule',
  'Find all overdue tasks',
  'Generate my productivity report',
  'Break down my project into tasks',
];

interface CommandInputProps {
  onSubmit: (command: string) => void;
  isLoading?: boolean;
}

export function CommandInput({ onSubmit, isLoading }: CommandInputProps) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSubmit(trimmed);
    setValue('');
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  return (
    <div className="relative">
      <div className={`bg-surface-card border rounded-2xl transition-all duration-200 ${focused ? 'border-accent/60 shadow-lg shadow-accent/10' : 'border-surface-border'}`}>
        <div className="flex items-start gap-3 p-4">
          <Zap className="w-5 h-5 text-accent mt-1 shrink-0" />
          <textarea
            ref={inputRef}
            rows={1}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKey}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask LifeOS anything... (Shift+Enter for new line)"
            className="flex-1 bg-transparent resize-none text-text-primary placeholder-text-muted text-sm focus:outline-none max-h-32"
            style={{ fieldSizing: 'content' } as React.CSSProperties}
          />
          <button
            onClick={handleSubmit}
            disabled={!value.trim() || isLoading}
            className="shrink-0 p-2 rounded-xl bg-accent hover:bg-accent-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>

        {focused && (
          <div className="border-t border-surface-border px-4 py-2 flex gap-2 flex-wrap">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onMouseDown={(e) => { e.preventDefault(); setValue(s); inputRef.current?.focus(); }}
                className="text-xs px-3 py-1 rounded-full bg-surface-hover text-text-secondary hover:text-accent hover:bg-accent/10 border border-surface-border transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
