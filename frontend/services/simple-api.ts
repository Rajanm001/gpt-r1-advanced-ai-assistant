import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  async sendMessage(message: string): Promise<any> {
    try {
      console.log('🚀 Sending message to OpenRouter backend:', message);
      
      const response = await api.post('/api/v1/chat', {
        message: message
      });
      
      console.log('✅ Received response:', response.data);
      
      return {
        message: response.data.message,
        timestamp: response.data.timestamp,
        status: response.data.status || 'success'
      };
    } catch (error) {
      console.error('❌ Chat service error:', error);
      
      // If the main endpoint fails, try the alternative endpoint
      try {
        console.log('🔄 Trying alternative endpoint...');
        const fallbackResponse = await api.post('/api/chat', {
          message: message
        });
        return {
          message: fallbackResponse.data.message,
          timestamp: fallbackResponse.data.timestamp,
          status: 'success'
        };
      } catch (fallbackError) {
        console.error('❌ Fallback also failed:', fallbackError);
        throw error;
      }
    }
  },

  // Keep the streaming interface for compatibility but adapt it to work with our JSON API
  async *streamChat(request: any): AsyncGenerator<any, void, unknown> {
    try {
      const response = await this.sendMessage(request.message);
      
      // Yield conversation ID
      yield {
        type: 'conversation_id',
        conversation_id: request.conversation_id || 'default'
      };
      
      // Yield the complete content as a stream-like response
      yield {
        type: 'content',
        content: response.message
      };
      
      // Yield done signal
      yield {
        type: 'done',
        timestamp: response.timestamp
      };
      
    } catch (error) {
      console.error('❌ Stream chat error:', error);
      // Fallback response for any errors
      yield {
        type: 'conversation_id',
        conversation_id: request.conversation_id || 'default'
      };
      
      yield {
        type: 'content',
        content: 'I apologize, but I encountered an issue. However, I\'m still here to help! Could you please try your message again?'
      };
      
      yield {
        type: 'done',
        timestamp: new Date().toISOString()
      };
    }
  },
};

export const healthService = {
  async checkHealth(): Promise<any> {
    try {
      const response = await api.get('/api/v1/health');
      return response.data;
    } catch (error) {
      console.error('❌ Health check failed:', error);
      return { status: 'unhealthy', error: error };
    }
  }
};

// Legacy conversation service (for compatibility)
export const conversationService = {
  async getConversations(): Promise<any[]> {
    return [];
  },

  async getConversation(id: number): Promise<any> {
    return { id, title: 'Chat', messages: [] };
  },

  async createConversation(title: string = 'New Conversation'): Promise<any> {
    return { id: Date.now(), title, messages: [] };
  },

  async updateConversation(id: number, updates: any): Promise<any> {
    return { id, ...updates };
  },

  async deleteConversation(id: number): Promise<void> {
    // No-op for now
  },
};