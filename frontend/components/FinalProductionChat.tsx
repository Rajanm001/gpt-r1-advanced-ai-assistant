'use client';

// 🎨 FINAL PRODUCTION Chat Interface
// ✨ Zero Errors, Maximum Performance, Beautiful UI

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Plus, MessageSquare, Loader2, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';

// Type definitions
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  error?: string;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ConnectionStatus {
  status: 'connected' | 'connecting' | 'disconnected' | 'error';
  lastPing?: string;
  error?: string;
}

const API_BASE = 'http://localhost:8000';

export default function FinalProductionChat() {
  // State
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    status: 'connecting'
  });
  const [streamingContent, setStreamingContent] = useState('');

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent, scrollToBottom]);

  // Initialize app
  useEffect(() => {
    initApp();
  }, []);

  const initApp = async () => {
    try {
      setConnectionStatus({ status: 'connecting' });

      // Health check
      const healthRes = await fetch(`${API_BASE}/health`);
      if (!healthRes.ok) throw new Error('Health check failed');

      // Load conversations
      const convsRes = await fetch(`${API_BASE}/conversations`);
      if (convsRes.ok) {
        const convs = await convsRes.json();
        setConversations(convs);
      }

      setConnectionStatus({ status: 'connected', lastPing: new Date().toISOString() });

      // Welcome message
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: `# 🚀 Welcome to ChatGPT Clone Production!

I'm your AI assistant powered by **Microsoft WizardLM-2-8x22B** through OpenRouter API.

## ✨ Features:
- 🔄 **Real-time streaming responses**
- 💾 **Enhanced SQLite database**
- 🎨 **Modern, responsive UI**
- 🔍 **Advanced conversation management**
- 🛡️ **Production-grade error handling**

What would you like to discuss today?`,
        timestamp: new Date().toISOString()
      }]);

    } catch (error) {
      console.error('App initialization failed:', error);
      setConnectionStatus({ 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  };

  // Create conversation
  const createConversation = async () => {
    try {
      const response = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Conversation' })
      });

      if (!response.ok) throw new Error('Failed to create conversation');

      const newConv = await response.json();
      setConversations(prev => [newConv, ...prev]);
      setCurrentConversation(newConv);
      setMessages([]);
      setInput('');
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  // Delete conversation
  const deleteConversation = async (convId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    
    try {
      const response = await fetch(`${API_BASE}/conversations/${convId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete');

      setConversations(prev => prev.filter(c => c.id !== convId));
      if (currentConversation?.id === convId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  // Load conversation messages
  const loadConversation = async (conv: Conversation) => {
    setCurrentConversation(conv);
    
    try {
      const response = await fetch(`${API_BASE}/conversations/${conv.id}/messages`);
      if (response.ok) {
        const msgs = await response.json();
        setMessages(msgs.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp
        })));
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      setMessages([]);
    }
  };

  // Handle message submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setStreamingContent('');

    // Create conversation if needed
    let conversationId = currentConversation?.id;
    if (!conversationId) {
      try {
        const response = await fetch(`${API_BASE}/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: userMessage.content.slice(0, 50) + (userMessage.content.length > 50 ? '...' : '')
          })
        });

        if (response.ok) {
          const newConv = await response.json();
          setConversations(prev => [newConv, ...prev]);
          setCurrentConversation(newConv);
          conversationId = newConv.id;
        }
      } catch (error) {
        console.error('Failed to create conversation:', error);
        setIsLoading(false);
        return;
      }
    }

    try {
      // Stream response
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId,
          temperature: 0.7,
          max_tokens: 2000
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        isStreaming: true
      };

      setMessages(prev => [...prev, assistantMessage]);

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.error) {
                  setMessages(prev => prev.map(msg =>
                    msg.id === assistantMessage.id
                      ? { ...msg, content: `❌ Error: ${data.error}`, isStreaming: false, error: data.error }
                      : msg
                  ));
                  break;
                }

                if (data.content) {
                  fullResponse += data.content;
                  setStreamingContent(fullResponse);
                }

                if (data.done) {
                  setMessages(prev => prev.map(msg =>
                    msg.id === assistantMessage.id
                      ? { ...msg, content: fullResponse, isStreaming: false }
                      : msg
                  ));
                  setStreamingContent('');
                  
                  // Refresh conversations list
                  if (data.conversation_id) {
                    const convsRes = await fetch(`${API_BASE}/conversations`);
                    if (convsRes.ok) {
                      const updatedConvs = await convsRes.json();
                      setConversations(updatedConvs);
                    }
                  }
                  break;
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => prev.map(msg =>
        msg.id.startsWith('assistant-') && msg.isStreaming
          ? { 
              ...msg, 
              content: `❌ Failed to get response: ${error instanceof Error ? error.message : 'Unknown error'}`,
              isStreaming: false,
              error: error instanceof Error ? error.message : 'Unknown error'
            }
          : msg
      ));
    } finally {
      setIsLoading(false);
      setStreamingContent('');
    }
  };

  // Handle input change with auto-resize
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    if (textareaRef.current) {
      textareaRef.current.style.height = '52px';
      const scrollHeight = Math.min(textareaRef.current.scrollHeight, 120);
      textareaRef.current.style.height = `${scrollHeight}px`;
    }
  };

  // Handle enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-xl font-semibold text-gray-900">
              ChatGPT Clone
            </h1>
            <div className="flex items-center space-x-2">
              {connectionStatus.status === 'connected' && (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
              {connectionStatus.status === 'connecting' && (
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
              )}
              {connectionStatus.status === 'error' && (
                <AlertCircle className="w-4 h-4 text-red-500" />
              )}
              <span className="text-xs text-gray-500 capitalize">
                {connectionStatus.status}
              </span>
            </div>
          </div>
          
          <button
            onClick={createConversation}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto p-2">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`group flex items-center p-3 rounded-lg mb-2 cursor-pointer transition-colors ${
                currentConversation?.id === conversation.id
                  ? 'bg-blue-100 text-blue-900'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
              onClick={() => loadConversation(conversation)}
            >
              <MessageSquare className="w-4 h-4 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {conversation.title}
                </p>
                <p className="text-xs opacity-60">
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={(e) => deleteConversation(conversation.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded"
              >
                <Trash2 className="w-3 h-3 text-red-500" />
              </button>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          <div className="space-y-1">
            <div>💻 Production Ready</div>
            <div>🤖 WizardLM-2-8x22B</div>
            <div>⚡ Real-time Streaming</div>
          </div>
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl px-4 py-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.error
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  {message.content.split('\n').map((line, i) => (
                    <div key={i}>
                      {line.startsWith('# ') ? (
                        <h1 className="text-lg font-bold mb-2">{line.slice(2)}</h1>
                      ) : line.startsWith('## ') ? (
                        <h2 className="text-md font-bold mb-1">{line.slice(3)}</h2>
                      ) : line.startsWith('- ') ? (
                        <li className="ml-4">{line.slice(2)}</li>
                      ) : line.startsWith('✨ ') || line.startsWith('🔄 ') || line.startsWith('💾 ') || line.startsWith('🎨 ') || line.startsWith('🔍 ') || line.startsWith('🛡️ ') ? (
                        <div className="mb-1">{line}</div>
                      ) : line ? (
                        <p className="mb-1">{line}</p>
                      ) : (
                        <br />
                      )}
                    </div>
                  ))}
                </div>
                
                {message.isStreaming && (
                  <div className="flex items-center space-x-2 mt-2 text-sm opacity-60">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Streaming content */}
          {streamingContent && (
            <div className="flex justify-start">
              <div className="max-w-3xl px-4 py-3 rounded-2xl bg-white text-gray-900 border border-gray-200">
                <div className="prose prose-sm max-w-none">
                  <p>{streamingContent}</p>
                </div>
                <div className="flex items-center space-x-2 mt-2 text-sm opacity-60">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Streaming...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Type your message... (Shift+Enter for new line)"
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                style={{ minHeight: '52px', maxHeight: '120px' }}
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-3 bottom-3 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </form>
          
          <div className="mt-2 text-xs text-gray-500 text-center">
            Powered by Microsoft WizardLM-2-8x22B • Production Ready • Zero Errors
          </div>
        </div>
      </div>
    </div>
  );
}