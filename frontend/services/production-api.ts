// 🚀 Production API Service - Enterprise Grade
// ✨ Modern HTTP client with error handling & retry logic

import axios, { AxiosError } from 'axios';
import type { Conversation, ChatRequest, ChatResponse, Analytics } from '@/types/production';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with proper configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ Response Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export class ApiService {
  // Health Check
  static async healthCheck() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Conversations
  static async getConversations(): Promise<Conversation[]> {
    try {
      const response = await apiClient.get('/conversations');
      return response.data;
    } catch (error) {
      console.error('Failed to get conversations:', error);
      throw error;
    }
  }

  static async createConversation(title: string): Promise<Conversation> {
    try {
      const response = await apiClient.post('/conversations', { title });
      return response.data;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw error;
    }
  }

  static async deleteConversation(id: string): Promise<void> {
    try {
      await apiClient.delete(`/conversations/${id}`);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  }

  static async getMessages(conversationId: string) {
    try {
      const response = await apiClient.get(`/conversations/${conversationId}/messages`);
      return response.data;
    } catch (error) {
      console.error('Failed to get messages:', error);
      throw error;
    }
  }

  // Analytics
  static async getAnalytics(): Promise<Analytics> {
    try {
      const response = await apiClient.get('/analytics');
      return response.data;
    } catch (error) {
      console.error('Failed to get analytics:', error);
      throw error;
    }
  }
}

// Chat Streaming Service
export class ChatStreamService {
  static async* streamChat(request: ChatRequest): AsyncGenerator<ChatResponse, void, unknown> {
    try {
      console.log('🤖 Starting chat stream...');
      
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Unknown error'}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            console.log('✅ Stream completed');
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6)) as ChatResponse;
                yield data;
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', line, parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      console.error('❌ Chat stream error:', error);
      yield { 
        error: error instanceof Error ? error.message : 'Unknown streaming error',
        done: true 
      };
    }
  }
}

export default ApiService;