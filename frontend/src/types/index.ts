export interface RetrievedChunk {
  content: string;
  source?: string;
  score?: number;
  metadata?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  question?: string;
  answer: string;
  chunks?: RetrievedChunk[];
  isStreaming?: boolean;
  error?: string;
  timestamp: Date;
}

export interface ApiResponse {
  answer: string;
  chunks?: RetrievedChunk[];
}
