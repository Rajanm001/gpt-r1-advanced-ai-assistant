// 🎯 Production Type Definitions - Clean & Complete
// ✨ Modern TypeScript interfaces for ChatGPT Clone

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  error?: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  content?: string;
  done?: boolean;
  error?: string;
  conversation_id?: string;
}

export interface ConnectionStatus {
  status: 'connected' | 'connecting' | 'disconnected' | 'error';
  lastPing?: string;
  error?: string;
}

export interface Analytics {
  total_conversations: number;
  total_messages: number;
  user_messages: number;
  assistant_messages: number;
  avg_tokens_per_message: number;
  updated_at: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
  error_type?: string;
}