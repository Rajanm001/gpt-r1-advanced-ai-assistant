'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, Plus, MessageCircle, Settings, User, Bot, Menu, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  updated_at: Date;
}

export default function ChatGPTInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isConnected, setIsConnected] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages]);

  useEffect(() => {
    loadConversations();
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      setIsConnected(response.ok);
    } catch {
      setIsConnected(false);
    }
  };

  const loadConversations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/conversations');
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
        if (data.length > 0 && !currentConversation) {
          setCurrentConversation(data[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Conversation' })
      });
      
      if (response.ok) {
        const newConv = await response.json();
        setConversations(prev => [newConv, ...prev]);
        setCurrentConversation(newConv);
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || isLoading || !currentConversation) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message.trim(),
      timestamp: new Date()
    };

    // Add user message immediately
    setCurrentConversation(prev => prev ? {
      ...prev,
      messages: [...prev.messages, userMessage]
    } : null);

    setMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: currentConversation.id
        })
      });

      if (response.ok) {
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let assistantContent = '';

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '',
          timestamp: new Date()
        };

        setCurrentConversation(prev => prev ? {
          ...prev,
          messages: [...prev.messages, assistantMessage]
        } : null);

        while (reader) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
              try {
                const data = JSON.parse(line.substring(6));
                if (data.type === 'content' && data.content) {
                  assistantContent += data.content;
                  
                  setCurrentConversation(prev => {
                    if (!prev) return null;
                    const updatedMessages = [...prev.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    if (lastMessage && lastMessage.role === 'assistant') {
                      lastMessage.content = assistantContent;
                    }
                    return { ...prev, messages: updatedMessages };
                  });
                }
              } catch (e) {
                // Ignore parsing errors
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Connection Status */}
      <div className={`connection-status ${isConnected ? 'online' : 'offline'}`}>
        {isConnected ? '🟢 Connected' : '🔴 Offline'}
      </div>

      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden bg-gray-900 text-white flex flex-col`}>
        <div className="p-4 border-b border-gray-700">
          <button
            onClick={createNewConversation}
            className="w-full btn-primary flex items-center gap-2 justify-center"
          >
            <Plus size={18} />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-2">
          {conversations.map(conv => (
            <div
              key={conv.id}
              onClick={() => setCurrentConversation(conv)}
              className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                currentConversation?.id === conv.id
                  ? 'bg-gray-700 border-l-4 border-blue-500'
                  : 'bg-gray-800 hover:bg-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageCircle size={16} />
                <span className="truncate text-sm font-medium">{conv.title}</span>
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {formatTime(new Date(conv.updated_at))}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3">
            <User size={20} />
            <span className="text-sm">User</span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center px-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <div className="flex-1 text-center">
            <h1 className="text-lg font-semibold gradient-text">
              {currentConversation?.title || 'ChatGPT Clone'}
            </h1>
          </div>

          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <Settings size={20} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
          {currentConversation?.messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <Bot size={32} className="text-white" />
                </div>
                <h2 className="text-2xl font-bold gradient-text mb-2">
                  How can I help you today?
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Start a conversation by typing your message below.
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6">
              {currentConversation?.messages.map(msg => (
                <div
                  key={msg.id}
                  className={`message-bubble flex gap-4 ${
                    msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-green-500 text-white'
                  }`}>
                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  
                  <div className={`max-w-[80%] ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`glass-morphism rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-500/20 border-blue-500/30'
                        : 'bg-white/50 dark:bg-gray-800/50 border-gray-200/30 dark:border-gray-700/30'
                    }`}>
                      {msg.role === 'assistant' ? (
                        <ReactMarkdown 
                          className="prose prose-sm dark:prose-invert max-w-none"
                          components={{
                            code: ({children}) => (
                              <code className="bg-gray-800 text-green-400 px-2 py-1 rounded text-sm">
                                {children}
                              </code>
                            ),
                            pre: ({children}) => (
                              <pre className="bg-gray-800 text-green-400 p-4 rounded-lg overflow-x-auto">
                                {children}
                              </pre>
                            )
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        <p className="text-sm leading-relaxed">{msg.content}</p>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTime(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center">
                    <Bot size={16} />
                  </div>
                  <div className="glass-morphism rounded-2xl px-4 py-3 bg-white/50 dark:bg-gray-800/50">
                    <div className="loading-dots text-gray-600">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="enhanced-input resize-none min-h-[50px] max-h-[200px] pr-12"
                rows={1}
                disabled={isLoading || !isConnected}
              />
              
              <button
                onClick={sendMessage}
                disabled={!message.trim() || isLoading || !isConnected}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 hover:scale-105"
              >
                <Send size={16} />
              </button>
            </div>
            
            <div className="text-xs text-gray-500 text-center mt-2">
              {isConnected ? (
                <>Press <kbd className="px-1 bg-gray-100 dark:bg-gray-700 rounded">Enter</kbd> to send, <kbd className="px-1 bg-gray-100 dark:bg-gray-700 rounded">Shift+Enter</kbd> for new line</>
              ) : (
                <span className="text-red-500">⚠️ Connection lost - Please refresh</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}