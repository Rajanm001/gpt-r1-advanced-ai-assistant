import axios from 'axios';
import { Conversation, ChatRequest } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const conversationService = {
  async getConversations(): Promise<Conversation[]> {
    const response = await api.get('/conversations');
    return response.data;
  },

  async getConversation(id: number): Promise<Conversation> {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },

  async createConversation(title: string = 'New Conversation'): Promise<Conversation> {
    const response = await api.post('/conversations', { title });
    return response.data;
  },

  async updateConversation(id: number, updates: Partial<Conversation>): Promise<Conversation> {
    const response = await api.patch(`/conversations/${id}`, updates);
    return response.data;
  },

  async deleteConversation(id: number): Promise<void> {
    await api.delete(`/conversations/${id}`);
  },
};

export const chatService = {
  async *streamChat(request: ChatRequest): AsyncGenerator<any, void, unknown> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data;
            } catch (e) {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};