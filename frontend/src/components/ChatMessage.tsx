// import type { RetrievedChunk } from '../types';
// import { SourceChunk } from './SourceChunk';

// interface Message {
//   id: string;
//   role: 'user' | 'assistant';
//   question?: string;
//   answer: string;
//   chunks?: RetrievedChunk[];
//   isStreaming?: boolean;
//   error?: string;
// }

// export function ChatMessage({ message }: { message: Message }) {
//   if (message.role === 'user') {
//     return (
//       <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '20px' }}>
//         <div style={{
//           maxWidth: '70%',
//           padding: '12px 18px',
//           borderRadius: '20px 20px 4px 20px',
//           background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
//           color: '#f0f0f5',
//           fontSize: '14px',
//           lineHeight: '1.6',
//           boxShadow: '0 2px 16px rgba(26,26,46,0.18)',
//           fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
//         }}>
//           {message.question}
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', alignItems: 'flex-start' }}>
//       {/* Avatar */}
//       <div style={{
//         width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
//         background: 'linear-gradient(135deg, #a8c5fa 0%, #c4b5fd 100%)',
//         display: 'flex', alignItems: 'center', justifyContent: 'center',
//         boxShadow: '0 2px 8px rgba(168,197,250,0.4)',
//         marginTop: '2px',
//       }}>
//         <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
//           <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
//         </svg>
//       </div>

//       <div style={{ flex: 1, minWidth: 0 }}>
//         {message.error ? (
//           <div style={{
//             padding: '12px 16px', borderRadius: '12px',
//             background: '#fff1f2', border: '1px solid #fecdd3',
//             color: '#be123c', fontSize: '13.5px', lineHeight: '1.6',
//             display: 'flex', gap: '10px', alignItems: 'flex-start',
//           }}>
//             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#be123c" strokeWidth="2" style={{ flexShrink: 0, marginTop: '1px' }}>
//               <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
//             </svg>
//             {message.error}
//           </div>
//         ) : (
//           <>
//             {/* Answer card */}
//             <div style={{
//               background: 'rgba(255,255,255,0.85)',
//               border: '1px solid rgba(0,0,0,0.07)',
//               borderRadius: '4px 16px 16px 16px',
//               padding: '16px 20px',
//               boxShadow: '0 1px 12px rgba(0,0,0,0.06)',
//               backdropFilter: 'blur(8px)',
//             }}>
//               <p style={{
//                 margin: 0,
//                 fontSize: '14.5px',
//                 lineHeight: '1.75',
//                 color: '#1a1a2e',
//                 fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
//                 whiteSpace: 'pre-wrap',
//               }}>
//                 {message.answer}
//                 {message.isStreaming && (
//                   <span style={{
//                     display: 'inline-block',
//                     width: '2px', height: '16px',
//                     background: '#6366f1',
//                     marginLeft: '3px',
//                     verticalAlign: 'text-bottom',
//                     animation: 'cursorBlink 1s step-end infinite',
//                   }} />
//                 )}
//               </p>
//             </div>

//             {/* Sources */}
//             {message.chunks && message.chunks.length > 0 && !message.isStreaming && (
//               <div style={{ marginTop: '12px' }}>
//                 <div style={{
//                   display: 'flex', alignItems: 'center', gap: '8px',
//                   marginBottom: '8px',
//                 }}>
//                   <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
//                     <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
//                   </svg>
//                   <span style={{
//                     fontSize: '11px', fontWeight: 700, letterSpacing: '0.08em',
//                     color: '#9ca3af', textTransform: 'uppercase',
//                   }}>
//                     Retrieved Context · {message.chunks.length} chunk{message.chunks.length !== 1 ? 's' : ''}
//                   </span>
//                   <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }} />
//                 </div>

//                 {message.chunks.map((chunk, i) => (
//                   <SourceChunk key={i} chunk={chunk} index={i} />
//                 ))}
//               </div>
//             )}
//           </>
//         )}
//       </div>
//     </div>
//   );
// }


import { SourceChunk } from './SourceChunk';

interface RetrievedChunk {
  content: string;
  source?: string;
  score?: number;
  metadata?: Record<string, unknown>;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  question?: string;
  answer: string;
  chunks?: RetrievedChunk[];
  isStreaming?: boolean;
  error?: string;
}

export function ChatMessage({ message }: { message: Message }) {
  if (message.role === 'user') {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '20px' }}>
        <div style={{
          maxWidth: '70%',
          padding: '12px 18px',
          borderRadius: '20px 20px 4px 20px',
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          color: '#f0f0f5',
          fontSize: '14px',
          lineHeight: '1.6',
          boxShadow: '0 2px 16px rgba(26,26,46,0.18)',
          fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        }}>
          {message.question}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', alignItems: 'flex-start' }}>
      {/* Avatar */}
      <div style={{
        width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
        background: 'linear-gradient(135deg, #a8c5fa 0%, #c4b5fd 100%)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 2px 8px rgba(168,197,250,0.4)',
        marginTop: '2px',
      }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
          <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
        </svg>
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        {message.error ? (
          <div style={{
            padding: '12px 16px', borderRadius: '12px',
            background: '#fff1f2', border: '1px solid #fecdd3',
            color: '#be123c', fontSize: '13.5px', lineHeight: '1.6',
            display: 'flex', gap: '10px', alignItems: 'flex-start',
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#be123c" strokeWidth="2" style={{ flexShrink: 0, marginTop: '1px' }}>
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {message.error}
          </div>
        ) : (
          <>
            {/* Answer card */}
            <div style={{
              background: 'rgba(255,255,255,0.85)',
              border: '1px solid rgba(0,0,0,0.07)',
              borderRadius: '4px 16px 16px 16px',
              padding: '16px 20px',
              boxShadow: '0 1px 12px rgba(0,0,0,0.06)',
              backdropFilter: 'blur(8px)',
            }}>
              <p style={{
                margin: 0,
                fontSize: '14.5px',
                lineHeight: '1.75',
                color: '#1a1a2e',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                whiteSpace: 'pre-wrap',
              }}>
                {message.answer}
                {message.isStreaming && (
                  <span style={{
                    display: 'inline-block',
                    width: '2px', height: '16px',
                    background: '#6366f1',
                    marginLeft: '3px',
                    verticalAlign: 'text-bottom',
                    animation: 'cursorBlink 1s step-end infinite',
                  }} />
                )}
              </p>
            </div>

            {/* Sources */}
            {message.chunks && message.chunks.length > 0 && !message.isStreaming && (
              <div style={{ marginTop: '12px' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '8px',
                  marginBottom: '8px',
                }}>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                  </svg>
                  <span style={{
                    fontSize: '11px', fontWeight: 700, letterSpacing: '0.08em',
                    color: '#9ca3af', textTransform: 'uppercase',
                  }}>
                    Retrieved Context · {message.chunks.length} chunk{message.chunks.length !== 1 ? 's' : ''}
                  </span>
                  <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }} />
                </div>

                {message.chunks.map((chunk, i) => (
                  <SourceChunk key={i} chunk={chunk} index={i} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
