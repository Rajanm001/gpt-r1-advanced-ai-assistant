export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
  conversation_history?: { role: string; content: string }[];
}

export interface StreamResponse {
  type: 'conversation_id' | 'content' | 'done' | 'error';
  conversation_id?: number;
  content?: string;
  error?: string;
}