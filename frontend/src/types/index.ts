export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: number;
  title?: string;
  user_id?: number;
  created_at: string;
  updated_at?: string;
  messages: Message[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
  use_rag?: boolean;
}

export interface ChatResponse {
  conversation_id: number;
  message: Message;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface StreamMessage {
  type: 'conversation_id' | 'context' | 'content' | 'done' | 'error';
  conversation_id?: number;
  content?: string;
  message_id?: number;
}

export interface ChatStore {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  
  // Actions
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  setLoading: (loading: boolean) => void;
  setStreaming: (streaming: boolean) => void;
  setError: (error: string | null) => void;
  createConversation: (title?: string) => Promise<Conversation>;
}

export interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}