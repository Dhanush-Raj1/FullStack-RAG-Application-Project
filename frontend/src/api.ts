// import { ApiResponse } from './types';

interface ApiResponse {
  answer: string;
  chunks?: { content: string; source?: string; score?: number }[];
}

interface UploadResult {
  filename: string;
  chunks_count: number;
  session_id: string;
}

const API_BASE = 'http://localhost:8000';

// Generate once per browser session
export const SESSION_ID = crypto.randomUUID();

export async function queryRAG(question: string): Promise<ApiResponse> {
  const res = await fetch(`${API_BASE}/api/chat/global`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function querySession(question: string): Promise<ApiResponse> {
  const res = await fetch(`${API_BASE}/api/chat/session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-session-id': SESSION_ID,
    },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function uploadFiles(files: File[]): Promise<UploadResult[]> {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    headers: { 'x-session-id': SESSION_ID },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  const data = await res.json();
  return data.uploaded;
}


// Simulates streaming — replace with real SSE if you add it to FastAPI
export async function* streamAnswer(
  text: string,
  chunkSize = 4,
  delayMs = 20
): AsyncGenerator<string> {
  for (let i = 0; i < text.length; i += chunkSize) {
    yield text.slice(i, i + chunkSize);
    await new Promise((r) => setTimeout(r, delayMs));
  }
}
