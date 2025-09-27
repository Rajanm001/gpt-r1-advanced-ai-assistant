'use client';

// 🎨 Production Chat Interface - Modern & Clean
// ✨ React 18 with hooks, proper error handling, and beautiful UI

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Plus, MessageSquare, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { ApiService, ChatStreamService } from '@/services/production-api';
import type { Message, Conversation, ConnectionStatus } from '@/types/production';

interface ChatInterfaceProps {
  className?: string;
}

export default function ProductionChatInterface({ className = '' }: ChatInterfaceProps) {
  // State Management
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
  const abortControllerRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent, scrollToBottom]);

  // Initialize app
  useEffect(() => {
    initializeApp();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const initializeApp = async () => {
    try {
      setConnectionStatus({ status: 'connecting' });
      
      // Health check
      await ApiService.healthCheck();
      
      // Load conversations
      const convs = await ApiService.getConversations();
      setConversations(convs);
      
      setConnectionStatus({ 
        status: 'connected', 
        lastPing: new Date().toISOString() 
      });

      // Show welcome message
      const welcomeMessage: Message = {
        id: 'welcome',
        role: 'assistant',
        content: `# 🚀 Welcome to ChatGPT Clone Production!

I'm your advanced AI assistant powered by **Microsoft WizardLM-2-8x22B** through OpenRouter API.

## ✨ Features:
- 🔄 **Real-time streaming responses**
- 💾 **PostgreSQL data persistence**
- 🎨 **Modern, responsive UI**
- 🔍 **Conversation management**
- 🛡️ **Enterprise-grade security**

How can I help you today?`,
        timestamp: new Date().toISOString()
      };

      setMessages([welcomeMessage]);
      
    } catch (error) {
      console.error('Initialization failed:', error);
      setConnectionStatus({ 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  };

  // Create new conversation
  const createConversation = async () => {
    try {
      const newConv = await ApiService.createConversation('New Conversation');
      setConversations(prev => [newConv, ...prev]);
      setCurrentConversation(newConv);
      setMessages([]);
      setInput('');
    } catch (error) {
      console.error('Failed to create conversation:', error);
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

    // Create conversation if none exists
    let conversationId = currentConversation?.id;
    if (!conversationId) {
      try {
        const newConv = await ApiService.createConversation(
          input.slice(0, 50) + (input.length > 50 ? '...' : '')
        );
        setConversations(prev => [newConv, ...prev]);
        setCurrentConversation(newConv);
        conversationId = newConv.id;
      } catch (error) {
        console.error('Failed to create conversation:', error);
        setIsLoading(false);
        return;
      }
    }

    try {
      // Abort previous request
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      let fullResponse = '';
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        isStreaming: true
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Stream the response
      for await (const chunk of ChatStreamService.streamChat({
        message: userMessage.content,
        conversation_id: conversationId
      })) {
        if (chunk.error) {
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: `❌ Error: ${chunk.error}`, isStreaming: false, error: chunk.error }
              : msg
          ));
          break;
        }

        if (chunk.content) {
          fullResponse += chunk.content;
          setStreamingContent(fullResponse);
        }

        if (chunk.done) {
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: fullResponse, isStreaming: false }
              : msg
          ));
          setStreamingContent('');
          
          if (chunk.conversation_id) {
            // Update conversation list
            setConversations(prev => 
              prev.map(conv => 
                conv.id === chunk.conversation_id 
                  ? { ...conv, updated_at: new Date().toISOString() }
                  : conv
              )
            );
          }
          break;
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage?.id 
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

  // Handle textarea auto-resize
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // Auto-resize
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
    <div className={`flex h-screen bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Sidebar */}
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
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
              <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                {connectionStatus.status}
              </span>
            </div>
          </div>
          
          <button
            onClick={createConversation}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-2">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => setCurrentConversation(conversation)}
              className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                currentConversation?.id === conversation.id
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <div className="flex items-start space-x-3">
                <MessageSquare className="w-4 h-4 mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {conversation.title}
                  </p>
                  <p className="text-xs opacity-60">
                    {new Date(conversation.updated_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
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
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
                    : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
                }`}
              >
                {message.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={oneDark}
                              language={match[1]}
                              PreTag="div"
                              customStyle={{ margin: 0, borderRadius: '8px' }}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                )}
                
                {message.isStreaming && (
                  <div className="flex items-center space-x-2 mt-2 text-sm opacity-60">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Streaming Content */}
          {streamingContent && (
            <div className="flex justify-start">
              <div className="max-w-3xl px-4 py-3 rounded-2xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {streamingContent}
                  </ReactMarkdown>
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

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Type your message here... (Shift+Enter for new line)"
                className="w-full px-4 py-3 pr-12 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
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
          
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
            <span>Powered by Microsoft WizardLM-2-8x22B via OpenRouter</span>
            {currentConversation && (
              <span>Conversation: {currentConversation.title}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}