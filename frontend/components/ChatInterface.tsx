'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Menu, Bot, User, Search, Globe, Zap, Mic, Image as ImageIcon, Sparkles, Activity, Wifi, WifiOff } from 'lucide-react';
import { Conversation, Message } from '@/types';
import { chatService } from '@/services/api';
import MessageBubble from './EnhancedMessageBubble';

interface ChatInterfaceProps {
  conversation: Conversation | null;
  onConversationCreated: (conversation: Conversation) => void;
  onToggleSidebar: () => void;
}

export default function ChatInterface({ 
  conversation, 
  onConversationCreated, 
  onToggleSidebar 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [useSearch, setUseSearch] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Check backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('disconnected');
        }
      } catch (error) {
        console.error('Connection check failed:', error);
        setConnectionStatus('disconnected');
      }
    };
    
    checkConnection();
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (conversation?.messages) {
      setMessages(conversation.messages);
    } else {
      setMessages([]);
      // Add welcome message for new conversations
      const welcomeMessage: Message = {
        id: -1,
        conversation_id: 0,
        role: 'assistant',
        content: '🚀 **Welcome to Advanced ChatGPT Clone!**\n\n✨ I\'m your AI assistant with enhanced capabilities:\n\n🔍 **Web Search Integration** - Toggle search for real-time information\n💬 **Intelligent Responses** - Advanced conversation understanding  \n🎨 **Creative Assistance** - Help with writing, coding, and analysis\n⚡ **Fast Processing** - Optimized for quick responses\n🌐 **Always Available** - Works even with network limitations\n\nHow can I help you today?',
        timestamp: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
    }
    setStreamingContent('');
  }, [conversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = '52px';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(scrollHeight, 120) + 'px';
    }
  }, [input]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setIsTyping(true);
    setConnectionStatus('connecting');
    setStreamingContent('');

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now(),
      conversation_id: conversation?.id || 0,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const chatRequest = {
        message: userMessage,
        conversation_id: conversation?.id,
        use_search: useSearch,
        conversation_history: messages.map(m => ({
          role: m.role,
          content: m.content
        }))
      };

      let fullResponse = '';
      let conversationId = conversation?.id;
      setConnectionStatus('connected');

      for await (const data of chatService.streamChat(chatRequest)) {
        if (data.type === 'conversation_id') {
          conversationId = data.conversation_id;
          if (!conversation) {
            // This is a new conversation, we should update the parent
            const newConversation: Conversation = {
              id: conversationId || 0,
              title: userMessage.length > 50 ? userMessage.substring(0, 50) + '...' : userMessage,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              messages: [],
            };
            onConversationCreated(newConversation);
          }
        } else if (data.type === 'content') {
          fullResponse += data.content;
          setStreamingContent(fullResponse);
          setIsTyping(false);
        } else if (data.type === 'done') {
          // Add assistant message to messages
          const assistantMessage: Message = {
            id: Date.now() + 1,
            conversation_id: conversationId || 0,
            role: 'assistant',
            content: fullResponse,
            timestamp: new Date().toISOString(),
          };
          setMessages(prev => [...prev, assistantMessage]);
          setStreamingContent('');
        } else if (data.type === 'error') {
          console.error('Chat error:', data.error);
          setStreamingContent('');
          setConnectionStatus('disconnected');
          // Add fallback error message
          const errorMessage: Message = {
            id: Date.now() + 2,
            conversation_id: conversationId || 0,
            role: 'assistant',
            content: '⚠️ **Connection Issue Detected**\n\nI\'m experiencing some technical difficulties, but I\'m still here to help! This might be due to:\n\n• Network connectivity issues\n• Server maintenance\n• API limitations\n\n🚀 **Don\'t worry!** I\'m designed to work even with limited connectivity. Please try again in a moment!',
            timestamp: new Date().toISOString(),
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setStreamingContent('');
      setConnectionStatus('disconnected');
      
      // Enhanced fallback message
      const fallbackMessage: Message = {
        id: Date.now() + 3,
        conversation_id: conversation?.id || 0,
        role: 'assistant',
        content: `🤖 **AI Assistant Response** (Offline Mode)\n\nI understand you're asking about: "${userMessage}"\n\nWhile I'm experiencing connectivity issues, I can still help you! Here are some suggestions:\n\n• **For coding questions**: I can help with syntax, best practices, and debugging\n• **For writing**: I can assist with structure, grammar, and style\n• **For analysis**: I can provide frameworks and methodologies\n• **For creative tasks**: I can suggest approaches and techniques\n\nPlease try your question again, and I'll do my best to assist you! 🚀`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-400';
      case 'connecting': return 'text-yellow-400';
      case 'disconnected': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected': return <Wifi className="h-3 w-3" />;
      case 'connecting': return <Activity className="h-3 w-3 animate-pulse" />;
      case 'disconnected': return <WifiOff className="h-3 w-3" />;
      default: return <Wifi className="h-3 w-3" />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative overflow-hidden">
      {/* Animated background pattern */}
      <div className="absolute inset-0 grid-pattern opacity-20"></div>
      
      {/* Enhanced Header */}
      <div className="glass border-b border-gray-700/50 p-4 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onToggleSidebar}
              className="enhanced-button p-2 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl transition-all duration-300 hover:scale-105"
            >
              <Menu className="w-5 h-5 text-gray-300" />
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Bot className="h-8 w-8 text-green-400 floating" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full neon-glow"></div>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  {conversation?.title || 'Advanced AI Assistant'}
                </h1>
                <div className="flex items-center space-x-2 text-sm">
                  {getConnectionIcon()}
                  <span className={getConnectionStatusColor()}>
                    {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}
                  </span>
                  {useSearch && (
                    <div className="flex items-center space-x-1 text-green-400">
                      <Globe className="h-3 w-3" />
                      <span>Web Search Active</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setUseSearch(!useSearch)}
              className={`enhanced-button px-4 py-2 rounded-xl border transition-all duration-300 ${
                useSearch
                  ? 'bg-green-500/20 border-green-400 text-green-400 shadow-glow'
                  : 'bg-gray-700/50 border-gray-600 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              <div className="flex items-center space-x-2">
                {useSearch ? <Globe className="h-4 w-4" /> : <Search className="h-4 w-4" />}
                <span className="hidden sm:inline">Web Search</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Enhanced Messages Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
        {messages.length === 0 && !streamingContent && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-6 message-bubble">
              <div className="relative">
                <Bot className="w-16 h-16 mx-auto text-green-400 floating" />
                <Sparkles className="w-6 h-6 absolute -top-2 -right-2 text-yellow-400 animate-pulse" />
              </div>
              <div className="space-y-3">
                <h2 className="text-3xl font-bold text-white">How can I help you today?</h2>
                <p className="text-gray-400 text-lg">Start a conversation by typing a message below.</p>
                <div className="flex flex-wrap justify-center gap-2 mt-6">
                  <div className="modern-card px-4 py-2 bg-green-500/10 border border-green-400/30 text-green-400 text-sm">
                    💬 Natural Conversations
                  </div>
                  <div className="modern-card px-4 py-2 bg-blue-500/10 border border-blue-400/30 text-blue-400 text-sm">
                    🔍 Web Search
                  </div>
                  <div className="modern-card px-4 py-2 bg-purple-500/10 border border-purple-400/30 text-purple-400 text-sm">
                    🎨 Creative Tasks
                  </div>
                  <div className="modern-card px-4 py-2 bg-orange-500/10 border border-orange-400/30 text-orange-400 text-sm">
                    ⚡ Fast Responses
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {streamingContent && (
          <div className="flex items-start space-x-4 message-bubble">
            <div className="flex-shrink-0 w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center border border-green-400/30">
              <Bot className="w-5 h-5 text-green-400" />
            </div>
            <div className="flex-1">
              <div className="modern-card rounded-2xl px-6 py-4">
                <MessageBubble 
                  message={{
                    id: 0,
                    conversation_id: 0,
                    role: 'assistant',
                    content: streamingContent,
                    timestamp: new Date().toISOString()
                  }} 
                  isStreaming 
                />
              </div>
            </div>
          </div>
        )}

        {isTyping && !streamingContent && (
          <div className="flex items-start space-x-4 message-bubble">
            <div className="flex-shrink-0 w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center border border-green-400/30">
              <Bot className="w-5 h-5 text-green-400" />
            </div>
            <div className="modern-card rounded-2xl px-6 py-4 max-w-xs">
              <div className="typing-indicator text-green-400 text-lg"></div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Enhanced Input Area */}
      <div className="glass border-t border-gray-700/50 p-6 relative z-10">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-end space-x-4">
            {/* Enhanced Input Field */}
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                className="w-full bg-gray-800/50 text-white border border-gray-600/50 rounded-2xl px-6 py-4 pr-16 resize-none enhanced-focus smooth-transition"
                style={{
                  minHeight: '52px',
                  maxHeight: '120px',
                }}
                disabled={isLoading}
              />
              
              {/* Character counter and input status */}
              <div className="absolute bottom-2 right-16 flex items-center space-x-2 text-xs text-gray-500">
                <span>{input.length}/2000</span>
                {input.length > 1800 && (
                  <span className="text-yellow-400">⚠️</span>
                )}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex space-x-2">
              <button
                type="button"
                className="enhanced-button w-12 h-12 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl flex items-center justify-center text-gray-400 hover:text-white smooth-transition"
                title="Voice input (coming soon)"
              >
                <Mic className="h-5 w-5" />
              </button>

              <button
                type="button"
                className="enhanced-button w-12 h-12 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl flex items-center justify-center text-gray-400 hover:text-white smooth-transition"
                title="Image upload (coming soon)"
              >
                <ImageIcon className="h-5 w-5" />
              </button>

              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className={`enhanced-button w-12 h-12 rounded-xl flex items-center justify-center smooth-transition ${
                  !input.trim() || isLoading
                    ? 'bg-gray-700/50 border-gray-600/50 text-gray-500 cursor-not-allowed'
                    : 'bg-green-500 hover:bg-green-600 border-green-400 text-white shadow-glow hover:scale-105'
                }`}
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* Status bar */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-4">
              {useSearch && (
                <div className="flex items-center space-x-1 text-green-400">
                  <Globe className="h-3 w-3" />
                  <span>Web search enabled</span>
                </div>
              )}
              <div className="flex items-center space-x-1">
                <Zap className="h-3 w-3" />
                <span>Advanced AI mode</span>
              </div>
              <div className="flex items-center space-x-1">
                <Sparkles className="h-3 w-3" />
                <span>Creative intelligence active</span>
              </div>
            </div>
            
            <div className="text-right">
              <span>Enhanced ChatGPT Clone v2.0</span>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}