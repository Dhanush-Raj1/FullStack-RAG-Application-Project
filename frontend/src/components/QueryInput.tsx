import { useState, useRef, type KeyboardEvent } from 'react';
import { Send, AlertCircle } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [value, setValue] = useState('');
  const [error, setError] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed) {
      setError('Please enter a question before sending.');
      textareaRef.current?.focus();
      return;
    }
    setError('');
    onSubmit(trimmed);
    setValue('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    if (error) setError('');
    // Auto-resize
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
  };

  return (
    <div className="space-y-2">
      {error && (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-950/50 border border-red-800/40 animate-slide-in">
          <AlertCircle size={13} className="text-red-400 flex-shrink-0" />
          <span className="text-xs text-red-300">{error}</span>
        </div>
      )}

      <div
        className="flex items-end gap-3 px-4 py-3 rounded-2xl transition-all duration-200"
        style={{
          background: 'rgba(9, 15, 31, 0.95)',
          border: error
            ? '1px solid rgba(239,68,68,0.4)'
            : '1px solid rgba(79,142,247,0.2)',
          boxShadow: error
            ? '0 0 0 3px rgba(239,68,68,0.06)'
            : '0 0 0 0px transparent',
        }}
        onFocus={() => {
          const el = document.querySelector('.input-wrapper') as HTMLElement;
          if (el) el.style.boxShadow = '0 0 0 3px rgba(79,142,247,0.08)';
        }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your documents..."
          disabled={isLoading}
          rows={1}
          className="flex-1 bg-transparent resize-none outline-none text-sm text-slate-200 placeholder:text-slate-600 leading-relaxed disabled:opacity-50 font-sans"
          style={{ maxHeight: '160px', minHeight: '24px' }}
        />

        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            background: isLoading
              ? 'rgba(79,142,247,0.15)'
              : 'linear-gradient(135deg, #3b76e0 0%, #2558c0 100%)',
            boxShadow: isLoading ? 'none' : '0 2px 12px rgba(79,142,247,0.3)',
          }}
          aria-label="Send message"
        >
          {isLoading ? (
            <div className="w-4 h-4 rounded-full border-2 border-accent/30 border-t-accent animate-spin" />
          ) : (
            <Send size={15} className="text-white translate-x-px" />
          )}
        </button>
      </div>

      <p className="text-xs text-slate-700 text-center">
        Press <kbd className="font-mono bg-navy-800 text-slate-600 px-1.5 py-0.5 rounded text-xs border border-white/5">Enter</kbd> to send
        {' · '}
        <kbd className="font-mono bg-navy-800 text-slate-600 px-1.5 py-0.5 rounded text-xs border border-white/5">Shift + Enter</kbd> for new line
      </p>
    </div>
  );
}
