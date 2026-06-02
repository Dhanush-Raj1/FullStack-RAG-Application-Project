import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { ChatMessage } from './components/ChatMessage';
import { queryRAG, querySession, streamAnswer, uploadFiles } from './api';


interface ChatMessageType {
  id: string;
  role: 'user' | 'assistant';
  question?: string;
  answer: string;
  chunks?: { content: string; source?: string; score?: number }[];
  isStreaming?: boolean;
  error?: string;
  timestamp: Date;
}

let counter = 0;
const uid = () => `m${++counter}_${Date.now()}`;

const HINTS = [
  'What are the key findings in this document?',
  'Summarize the main topics covered.',
  'What conclusions does the author draw?',
];

export default function App() {
  const [pendingFiles, setPendingFiles] = useState<{name: string; type: string; status: 'uploading' | 'done' | 'error'}[]>([]);
  const [sessionReady, setSessionReady] = useState(false);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [inputError, setInputError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  
  const handleSubmit = async (question?: string) => {
  const q = (question ?? input).trim();
  if (!q) {
    setInputError('Please type a question first.');
    textareaRef.current?.focus();
    return;
  }
  setInputError('');
  setInput('');
  setPendingFiles([]);  // ← clears file chips on send
  if (textareaRef.current) textareaRef.current.style.height = 'auto';

  const userMsg: ChatMessageType = {
    id: uid(), role: 'user', question: q, answer: q, timestamp: new Date(),
  };
  const aId = uid();
  const assistantMsg: ChatMessageType = {
    id: aId, role: 'assistant', answer: '', isStreaming: true, timestamp: new Date(),
  };

  setMessages(prev => [...prev, userMsg, assistantMsg]);
  setLoading(true);

  try {
    const data = sessionReady ? await querySession(q) : await queryRAG(q);
    let streamed = '';
    for await (const chunk of streamAnswer(data.answer)) {
      streamed += chunk;
      const snap = streamed;
      setMessages(prev => prev.map(m => m.id === aId ? { ...m, answer: snap } : m));
    }
    setMessages(prev => prev.map(m =>
      m.id === aId ? { ...m, answer: data.answer, isStreaming: false, chunks: data.chunks } : m
    ));
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Something went wrong.';
    setMessages(prev => prev.map(m =>
      m.id === aId ? { ...m, answer: '', isStreaming: false, error: msg } : m
    ));
  } finally {
    setLoading(false);
  }
};

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (inputError) setInputError('');
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px';
  };

  const isEmpty = messages.length === 0;

  return (
    <>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body, #root { height: 100%; }
        body {
          font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
          -webkit-font-smoothing: antialiased;
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes cursorBlink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 8px rgba(139,92,246,0.4); }
          50% { box-shadow: 0 0 18px rgba(139,92,246,0.8); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-6px); }
        }
        .hint-btn:hover {
          background: rgba(255,255,255,0.85) !important;
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(99,102,241,0.15) !important;
          border-color: rgba(99,102,241,0.3) !important;
        }
        .hint-btn { transition: all 0.25s ease; }
        .send-btn:hover:not(:disabled) {
          transform: scale(1.05);
          box-shadow: 0 6px 24px rgba(99,102,241,0.55) !important;
        }
        .send-btn { transition: all 0.2s ease; }
        .input-wrap:focus-within {
          border-color: rgba(139,92,246,0.5) !important;
          box-shadow: 0 0 0 4px rgba(139,92,246,0.08), 0 8px 32px rgba(0,0,0,0.1) !important;
        }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.2); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.4); }
      `}</style>


        <div style={{
          display: 'flex', flexDirection: 'column', height: '100vh',
          position: 'relative', overflow: 'hidden',
          background: '#fafafa',
        }}>
          {/* Mesh gradient background */}
          <div style={{
            position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none',
            background: `
              radial-gradient(ellipse 80% 60% at 20% -10%, rgba(139,92,246,0.18) 0%, transparent 60%),
              radial-gradient(ellipse 60% 50% at 80% 10%, rgba(99,102,241,0.12) 0%, transparent 55%),
              radial-gradient(ellipse 70% 60% at 50% 100%, rgba(168,85,247,0.1) 0%, transparent 60%),
              radial-gradient(ellipse 50% 40% at 0% 60%, rgba(59,130,246,0.08) 0%, transparent 50%),
              radial-gradient(ellipse 40% 30% at 100% 50%, rgba(236,72,153,0.06) 0%, transparent 50%)
            `,
          }} />
          {/* Subtle grid texture */}
          <div style={{
            position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', opacity: 0.4,
            backgroundImage: `linear-gradient(rgba(139,92,246,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.04) 1px, transparent 1px)`,
            backgroundSize: '48px 48px',
          }} />

        {/* Header */}
        <header style={{
          position: 'relative', zIndex: 10,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '14px 28px',
          background: 'rgba(255,255,255,0.7)',
          backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
          borderBottom: '1px solid rgba(139,92,246,0.1)',
          boxShadow: '0 1px 0 rgba(255,255,255,0.8), 0 4px 24px rgba(139,92,246,0.06)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Logo mark */}
            <div style={{
              width: '38px', height: '38px', borderRadius: '12px',
              background: 'linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #4f46e5 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 16px rgba(124,58,237,0.4)',
              animation: 'pulse-glow 3s ease-in-out infinite',
              flexShrink: 0,
            }}>
              {/* Sparkle / AI icon */}
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" fill="white" opacity="0.95"/>
                <path d="M19 16L19.75 18.25L22 19L19.75 19.75L19 22L18.25 19.75L16 19L18.25 18.25L19 16Z" fill="white" opacity="0.7"/>
                <path d="M5 3L5.5 4.5L7 5L5.5 5.5L5 7L4.5 5.5L3 5L4.5 4.5L5 3Z" fill="white" opacity="0.6"/>
              </svg>
            </div>
            <div>
              <div style={{
                fontSize: '16px', fontWeight: 800, color: '#0f0a1e',
                letterSpacing: '-0.04em', lineHeight: '1.2',
              }}>
                Docs<span style={{ color: '#7c3aed' }}>AI</span>
              </div>
              <div style={{
                fontSize: '10.5px', color: '#7c3aed', marginTop: '2px',
                fontWeight: 500, letterSpacing: '0.04em', textTransform: 'uppercase',
                opacity: 0.7,
              }}>
                Document Intelligence
              </div>
            </div>
          </div>
            
          {/* Status badge */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '7px',
            padding: '6px 14px 6px 10px',
            background: 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(5,150,105,0.05) 100%)',
            border: '1px solid rgba(16,185,129,0.2)',
            borderRadius: '50px',
            boxShadow: '0 1px 8px rgba(16,185,129,0.08)',
          }}>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '7px', height: '7px', borderRadius: '50%', background: '#10b981',
                boxShadow: '0 0 0 0 rgba(16,185,129,0.4)',
                animation: 'cursorBlink 2.5s ease-in-out infinite',
              }} />
            </div>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#059669', letterSpacing: '0.01em' }}>
              Ready
            </span>
          </div>
        </header>

        {/* Main */}
        <main style={{flex: 1, overflowY: 'auto', position: 'relative', zIndex: 1,}}>

          {isEmpty ? (
            /* Empty state */
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center',
              justifyContent: 'center', height: '100%', padding: '40px 20px',
              textAlign: 'center', animation: 'fadeUp 0.5s ease both',
            }}>
              {/* Floating icon */}
              <div style={{
                width: '72px', height: '72px', borderRadius: '24px', marginBottom: '28px',
                background: 'linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #4f46e5 100%)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 12px 40px rgba(124,58,237,0.35)',
                animation: 'float 4s ease-in-out infinite',
              }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" fill="white"/>
                  <path d="M19 16L19.75 18.25L22 19L19.75 19.75L19 22L18.25 19.75L16 19L18.25 18.25L19 16Z" fill="white" opacity="0.7"/>
                  <path d="M5 3L5.5 4.5L7 5L5.5 5.5L5 7L4.5 5.5L3 5L4.5 4.5L5 3Z" fill="white" opacity="0.6"/>
                </svg>
              </div>            

              <h2 style={{
                fontSize: '32px', fontWeight: 800, color: '#0f0a1e',
                letterSpacing: '-0.05em', marginBottom: '12px', lineHeight: '1.15',
              }}>
                What do you want to<br />
                <span style={{
                  background: 'linear-gradient(135deg, #7c3aed, #6366f1)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>explore today?</span>
              </h2>
              <p style={{
                fontSize: '14px', color: '#6b7280', maxWidth: '360px',
                lineHeight: '1.7', marginBottom: '36px',
              }}>
                Upload your documents or ask from the knowledge base.
                Powered by pgvector, Gemini, and Cohere reranking.
              </p>            

              <div style={{
                display: 'flex', flexWrap: 'wrap', gap: '10px',
                justifyContent: 'center', maxWidth: '580px',
              }}>
                {HINTS.map(h => (
                  <button
                    key={h}
                    className="hint-btn"
                    onClick={() => handleSubmit(h)}
                    style={{
                      padding: '10px 20px', borderRadius: '50px',
                      background: 'rgba(255,255,255,0.75)',
                      border: '1px solid rgba(139,92,246,0.15)',
                      color: '#374151', fontSize: '13px', cursor: 'pointer',
                      boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
                      backdropFilter: 'blur(12px)',
                      fontWeight: 500,
                    }}
                  >
                    {h}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ maxWidth: '760px', margin: '0 auto', padding: '28px 20px' }}>
              {messages.map(msg => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </main>

        {/* Input footer */}
        <footer style={{
          position: 'relative', zIndex: 10,
          padding: '12px 20px 20px',
          background: 'rgba(255,255,255,0.6)',
          backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
          borderTop: '1px solid rgba(139,92,246,0.08)',
          boxShadow: '0 -1px 0 rgba(255,255,255,0.8)',
        }}>
          <div style={{ maxWidth: '760px', margin: '0 auto' }}>
            {inputError && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '8px 12px', borderRadius: '10px', marginBottom: '8px',
                background: '#fff1f2', border: '1px solid #fecdd3',
                animation: 'fadeUp 0.2s ease both',
              }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#be123c" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span style={{ fontSize: '12.5px', color: '#be123c' }}>{inputError}</span>
              </div>
            )}

            {/* <div style={{
              background: 'rgba(255,255,255,0.9)',
              border: inputError ? '1.5px solid #fca5a5' : '1.5px solid rgba(99,102,241,0.25)',
              borderRadius: '20px',
              boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
              overflow: 'hidden',
            }}> */}

            <div
              className="input-wrap"
              style={{
                background: 'rgba(255,255,255,0.82)',
                border: inputError ? '1.5px solid #fca5a5' : '1.5px solid rgba(139,92,246,0.2)',
                borderRadius: '20px',
                boxShadow: '0 8px 32px rgba(139,92,246,0.1), 0 1px 0 rgba(255,255,255,0.9) inset',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                overflow: 'hidden',
                transition: 'border-color 0.2s, box-shadow 0.2s',
              }}
            >
            
              {/* File chips row — shown only when files are pending/done */}
              {pendingFiles.length > 0 && (
                <div style={{
                  display: 'flex', gap: '10px', padding: '10px 12px 4px',
                  flexWrap: 'wrap',
                }}>
                  {pendingFiles.map((f, i) => {
                    const isPdf = f.name.toLowerCase().endsWith('.pdf');
                    const isDone = f.status === 'done';
                    const isUploading = f.status === 'uploading';
                    const ext = f.name.split('.').pop()?.toUpperCase() || 'FILE';
                    const shortName = f.name.length > 22 ? f.name.slice(0, 20) + '…' : f.name;
                  
                    return (
                      <div key={i} style={{
                        display: 'flex', alignItems: 'center', gap: '10px',
                        padding: '8px 10px',
                        borderRadius: '12px',
                        border: '1px solid',
                        borderColor: isDone
                          ? (isPdf ? 'rgba(239,68,68,0.2)' : 'rgba(59,130,246,0.2)')
                          : 'rgba(0,0,0,0.08)',
                        background: isDone
                          ? (isPdf ? 'rgba(254,242,242,0.9)' : 'rgba(239,246,255,0.9)')
                          : 'rgba(0,0,0,0.04)',
                        opacity: isUploading ? 0.5 : 1,
                        transition: 'all 0.3s ease',
                        minWidth: '160px', maxWidth: '220px',
                      }}>
                        {/* File type icon */}
                        <div style={{
                          width: '36px', height: '36px', borderRadius: '8px', flexShrink: 0,
                          background: isUploading
                            ? '#d1d5db'
                            : isPdf
                              ? 'linear-gradient(135deg, #ef4444, #dc2626)'
                              : 'linear-gradient(135deg, #3b82f6, #2563eb)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          transition: 'background 0.3s ease',
                          boxShadow: isDone
                            ? (isPdf ? '0 2px 8px rgba(239,68,68,0.35)' : '0 2px 8px rgba(59,130,246,0.35)')
                            : 'none',
                        }}>
                          {isUploading ? (
                            <div style={{
                              width: '14px', height: '14px', borderRadius: '50%',
                              border: '2px solid rgba(255,255,255,0.3)',
                              borderTop: '2px solid white',
                              animation: 'spin 0.7s linear infinite',
                            }} />
                          ) : isPdf ? (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                              <polyline points="14 2 14 8 20 8" fill="none" stroke="white" strokeWidth="1.5"/>
                              <line x1="8" y1="13" x2="16" y2="13" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5"/>
                              <line x1="8" y1="17" x2="13" y2="17" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5"/>
                            </svg>
                          ) : (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                              <polyline points="14 2 14 8 20 8" fill="none" stroke="white" strokeWidth="1.5"/>
                              <line x1="8" y1="13" x2="16" y2="13" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5"/>
                              <line x1="8" y1="17" x2="13" y2="17" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5"/>
                            </svg>
                          )}
                        </div>
                        
                        {/* Name + type */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{
                            margin: 0, fontSize: '12.5px', fontWeight: 600,
                            color: isDone ? '#1a1a2e' : '#9ca3af',
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                            transition: 'color 0.3s ease',
                          }}>
                            {shortName}
                          </p>
                          <p style={{
                            margin: 0, fontSize: '10.5px',
                            color: isUploading ? '#9ca3af' : (isPdf ? '#ef4444' : '#3b82f6'),
                            marginTop: '1px', fontWeight: 500,
                            transition: 'color 0.3s ease',
                          }}>
                            {isUploading ? 'Processing…' : ext}
                          </p>
                        </div>
                        
                        {/* Remove X */}
                        {!isUploading && (
                          <button
                            onClick={() => setPendingFiles(prev => prev.filter((_, j) => j !== i))}
                            style={{
                              width: '20px', height: '20px', borderRadius: '50%', flexShrink: 0,
                              background: 'rgba(0,0,0,0.15)', border: 'none', cursor: 'pointer',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              padding: 0,
                            }}
                          >
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Input row */}
              <div style={{
                display: 'flex', alignItems: 'flex-end', gap: '8px',
                padding: pendingFiles.length > 0 ? '4px 10px 8px 12px' : '8px 10px 8px 8px',
              }}>
                {/* + button */}
                <div style={{ position: 'relative', flexShrink: 0 }}>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.md,.txt"
                    style={{ display: 'none' }}
                    id="inline-file-input"
                    onChange={async (e) => {
                      const selected = Array.from(e.target.files || []);
                      if (!selected.length) return;
                    
                      const MAX_FILES = 3;
                      const MAX_BYTES = 10 * 1024 * 1024;
                      const ALLOWED = ['.pdf', '.md', '.txt'];
                    
                      const currentCount = pendingFiles.filter(f => f.status !== 'error').length;
                      if (currentCount + selected.length > MAX_FILES) {
                        setInputError(`Maximum ${MAX_FILES} files allowed.`);
                        return;
                      }
                      for (const f of selected) {
                        const ext = '.' + f.name.split('.').pop()?.toLowerCase();
                        if (!ALLOWED.includes(ext)) {
                          setInputError(`"${f.name}" not supported. Use PDF, MD, or TXT.`);
                          return;
                        }
                        if (f.size > MAX_BYTES) {
                          setInputError(`"${f.name}" exceeds 10MB limit.`);
                          return;
                        }
                      }
                    
                      setInputError('');
                    
                      // Add chips in uploading state immediately
                      const newChips = selected.map(f => ({
                        name: f.name,
                        type: f.name.split('.').pop()?.toLowerCase() || 'file',
                        status: 'uploading' as const,
                      }));
                      setPendingFiles(prev => [...prev, ...newChips]);
                    
                      try {
                        await uploadFiles(selected);
                        setSessionReady(true);
                        // Transition chips to done
                        setPendingFiles(prev => prev.map(chip =>
                          newChips.find(n => n.name === chip.name)
                            ? { ...chip, status: 'done' }
                            : chip
                        ));
                      } catch (err) {
                        setInputError(err instanceof Error ? err.message : 'Upload failed.');
                        setPendingFiles(prev => prev.map(chip =>
                          newChips.find(n => n.name === chip.name)
                            ? { ...chip, status: 'error' }
                            : chip
                        ));
                      } finally {
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => document.getElementById('inline-file-input')?.click()}
                    title="Upload documents (PDF, MD, TXT)"
                    style={{
                      width: '36px', height: '36px', borderRadius: '10px',
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#9ca3af',
                      transition: 'color 0.2s ease',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.color = '#6366f1')}
                    onMouseLeave={e => (e.currentTarget.style.color = '#9ca3af')}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </div>
                  
                {/* Textarea */}
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask anything about your documents..."
                  disabled={loading}
                  rows={1}
                  style={{
                    flex: 1, background: 'transparent', border: 'none', outline: 'none',
                    resize: 'none', fontSize: '14px', lineHeight: '1.6', color: '#1a1a2e',
                    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                    minHeight: '24px', maxHeight: '140px',
                    opacity: loading ? 0.5 : 1,
                    padding: '7px 4px',
                  }}
                />

                {/* Send */}
                <button
                  className="send-btn"
                  onClick={() => handleSubmit()}
                  disabled={loading}
                  style={{
                    width: '38px', height: '38px', borderRadius: '12px', flexShrink: 0,
                    background: loading ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: loading ? 'none' : '0 2px 12px rgba(99,102,241,0.35)',
                  }}
                >
                  {loading ? (
                    <div style={{
                      width: '16px', height: '16px', borderRadius: '50%',
                      border: '2px solid rgba(255,255,255,0.3)',
                      borderTop: '2px solid white',
                      animation: 'spin 0.7s linear infinite',
                    }} />
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="white" style={{ transform: 'translateX(1px)' }}>
                      <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>
                
            <p style={{
              textAlign: 'center', fontSize: '11px', color: '#d1d5db',
              marginTop: '8px',
            }}>
              Press <span style={{ fontFamily: 'monospace', background: '#f3f4f6', padding: '1px 5px', borderRadius: '4px', color: '#9ca3af' }}>Enter</span> to send
              {' · '}
              <span style={{ fontFamily: 'monospace', background: '#f3f4f6', padding: '1px 5px', borderRadius: '4px', color: '#9ca3af' }}>Shift+Enter</span> for new line
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
