// import { useState } from 'react';
// import type { RetrievedChunk } from '../types';

// interface Props {
//   chunk: RetrievedChunk;
//   index: number;
// }

// export function SourceChunk({ chunk, index }: Props) {
//   const [open, setOpen] = useState(index === 0);

//   return (
//     <div
//       style={{
//         border: '1px solid #d1e8d4',
//         borderRadius: '12px',
//         overflow: 'hidden',
//         background: '#f0faf2',
//         marginBottom: '8px',
//         animation: `fadeUp 0.3s ease both`,
//         animationDelay: `${index * 60}ms`,
//       }}
//     >
//       <button
//         onClick={() => setOpen(!open)}
//         style={{
//           width: '100%',
//           display: 'flex',
//           alignItems: 'center',
//           justifyContent: 'space-between',
//           padding: '10px 14px',
//           background: 'transparent',
//           border: 'none',
//           cursor: 'pointer',
//           textAlign: 'left',
//           gap: '12px',
//         }}
//       >
//         <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
//           {/* Icon */}
//           <div style={{
//             width: '24px', height: '24px', borderRadius: '6px',
//             background: '#c6edd0', display: 'flex', alignItems: 'center',
//             justifyContent: 'center', flexShrink: 0,
//           }}>
//             <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#2d7a47" strokeWidth="2.5">
//               <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
//               <polyline points="14 2 14 8 20 8"/>
//             </svg>
//           </div>
//           <div style={{ minWidth: 0 }}>
//             <span style={{
//               fontSize: '10px', fontWeight: 700, letterSpacing: '0.1em',
//               color: '#2d7a47', textTransform: 'uppercase', display: 'block',
//             }}>
//               Source {String(index + 1).padStart(2, '0')}
//             </span>
//             {chunk.source && (
//               <span style={{
//                 fontSize: '11px', color: '#5aaa74', display: 'block',
//                 overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
//                 fontFamily: 'monospace',
//               }}>
//                 {chunk.source}
//               </span>
//             )}
//           </div>
//         </div>

//         <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
//           {chunk.score !== undefined && (
//             <span style={{
//               fontSize: '10px', fontFamily: 'monospace', color: '#5aaa74',
//               background: '#d6f0dc', padding: '2px 7px', borderRadius: '20px',
//             }}>
//               {(chunk.score * 100).toFixed(1)}%
//             </span>
//           )}
//           <svg
//             width="14" height="14" viewBox="0 0 24 24" fill="none"
//             stroke="#5aaa74" strokeWidth="2"
//             style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}
//           >
//             <polyline points="6 9 12 15 18 9"/>
//           </svg>
//         </div>
//       </button>

//       {open && (
//         <div style={{
//           padding: '4px 14px 12px',
//           borderTop: '1px solid #d1e8d4',
//         }}>
//           <p style={{
//             margin: 0,
//             fontSize: '12.5px',
//             lineHeight: '1.7',
//             color: '#2d5a3a',
//             fontFamily: '"SF Mono", "Fira Code", monospace',
//             whiteSpace: 'pre-wrap',
//           }}>
//             {chunk.content}
//           </p>
//         </div>
//       )}
//     </div>
//   );
// }

import { useState } from 'react';

interface RetrievedChunk {
  content: string;
  source?: string;
  score?: number;
  metadata?: Record<string, unknown>;
}

interface Props {
  chunk: RetrievedChunk;
  index: number;
}

export function SourceChunk({ chunk, index }: Props) {
  const [open, setOpen] = useState(index === 0);

  return (
    <div
      style={{
        border: '1px solid #d1e8d4',
        borderRadius: '12px',
        overflow: 'hidden',
        background: '#f0faf2',
        marginBottom: '8px',
        animation: `fadeUp 0.3s ease both`,
        animationDelay: `${index * 60}ms`,
      }}
    >
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
          {/* Icon */}
          <div style={{
            width: '24px', height: '24px', borderRadius: '6px',
            background: '#c6edd0', display: 'flex', alignItems: 'center',
            justifyContent: 'center', flexShrink: 0,
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#2d7a47" strokeWidth="2.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div style={{ minWidth: 0 }}>
            <span style={{
              fontSize: '10px', fontWeight: 700, letterSpacing: '0.1em',
              color: '#2d7a47', textTransform: 'uppercase', display: 'block',
            }}>
              Source {String(index + 1).padStart(2, '0')}
            </span>
            {chunk.source && (
              <span style={{
                fontSize: '11px', color: '#5aaa74', display: 'block',
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                fontFamily: 'monospace',
              }}>
                {chunk.source}
              </span>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
          {chunk.score !== undefined && (
            <span style={{
              fontSize: '10px', fontFamily: 'monospace', color: '#5aaa74',
              background: '#d6f0dc', padding: '2px 7px', borderRadius: '20px',
            }}>
              {(chunk.score * 100).toFixed(1)}%
            </span>
          )}
          <svg
            width="14" height="14" viewBox="0 0 24 24" fill="none"
            stroke="#5aaa74" strokeWidth="2"
            style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </button>

      {open && (
        <div style={{
          padding: '4px 14px 12px',
          borderTop: '1px solid #d1e8d4',
        }}>
          <p style={{
            margin: 0,
            fontSize: '12.5px',
            lineHeight: '1.7',
            color: '#2d5a3a',
            fontFamily: '"SF Mono", "Fira Code", monospace',
            whiteSpace: 'pre-wrap',
          }}>
            {chunk.content}
          </p>
        </div>
      )}
    </div>
  );
}
