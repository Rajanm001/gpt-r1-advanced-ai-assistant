"use client";'use client';



import React, { useState, useRef, useEffect } from 'react';import { useState, useRef, useEffect } from 'react';

import { Send, Loader2, MessageSquare, Plus, Bot, User, Moon, Sun } from 'lucide-react';import { Send, Menu, Bot, User, Search, Globe, Zap, Mic, Image as ImageIcon, Sparkles, Activity, Wifi, WifiOff } from 'lucide-react';

import { Conversation, Message } from '@/types';

interface Message {import { chatService } from '@/services/api';

  id: number;import MessageBubble from './EnhancedMessageBubble';

  role: 'user' | 'assistant';

  content: string;interface ChatInterfaceProps {

  timestamp: string;  conversation: Conversation | null;

  isStreaming?: boolean;  onConversationCreated: (conversation: Conversation) => void;

}  onToggleSidebar: () => void;

}

interface Conversation {

  id: string;export default function ChatInterface({ 

  title: string;  conversation, 

  created_at: string;  onConversationCreated, 

  updated_at: string;  onToggleSidebar 

}}: ChatInterfaceProps) {

  const [messages, setMessages] = useState<Message[]>([]);

const ChatInterface: React.FC = () => {  const [input, setInput] = useState('');

  const [messages, setMessages] = useState<Message[]>([]);  const [isLoading, setIsLoading] = useState(false);

  const [conversations, setConversations] = useState<Conversation[]>([]);  const [streamingContent, setStreamingContent] = useState('');

  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);  const [useSearch, setUseSearch] = useState(false);

  const [input, setInput] = useState('');  const [isTyping, setIsTyping] = useState(false);

  const [isLoading, setIsLoading] = useState(false);  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');

  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected');  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [darkMode, setDarkMode] = useState(true);  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const inputRef = useRef<HTMLInputElement>(null);  // Check backend connection on mount

  useEffect(() => {

  useEffect(() => {    const checkConnection = async () => {

    checkBackendHealth();      try {

    fetchConversations();        const response = await fetch('http://localhost:8000/health');

            if (response.ok) {

    // Add welcome message          setConnectionStatus('connected');

    const welcomeMessage: Message = {        } else {

      id: Date.now(),          setConnectionStatus('disconnected');

      role: 'assistant',        }

      content: '🚀 **Welcome to ChatGPT Clone!**\n\nI\'m your AI assistant powered by advanced language models. I can help you with:\n\n• ❓ **Answering Questions** - Any topic you\'re curious about\n• 💡 **Creative Writing** - Stories, poems, scripts\n• 🔧 **Problem Solving** - Technical and analytical tasks\n• 💬 **Conversations** - Just chat and explore ideas\n\n**Type your message below to start our conversation!**',      } catch (error) {

      timestamp: new Date().toISOString(),        console.error('Connection check failed:', error);

    };        setConnectionStatus('disconnected');

    setMessages([welcomeMessage]);      }

  }, []);    };

    

  useEffect(() => {    checkConnection();

    scrollToBottom();    // Check connection every 30 seconds

  }, [messages]);    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);

  const checkBackendHealth = async () => {  }, []);

    try {

      setConnectionStatus('connecting');  useEffect(() => {

      const response = await fetch('http://localhost:8000/health');    if (conversation?.messages) {

      const health = await response.json();      setMessages(conversation.messages);

      setConnectionStatus(health.status === 'healthy' ? 'connected' : 'disconnected');    } else {

    } catch (error) {      setMessages([]);

      console.error('Health check failed:', error);      // Add welcome message for new conversations

      setConnectionStatus('disconnected');      const welcomeMessage: Message = {

    }        id: -1,

  };        conversation_id: 0,

        role: 'assistant',

  const fetchConversations = async () => {        content: '🚀 **Welcome to Advanced ChatGPT Clone!**\n\n✨ I\'m your AI assistant with enhanced capabilities:\n\n🔍 **Web Search Integration** - Toggle search for real-time information\n💬 **Intelligent Responses** - Advanced conversation understanding  \n🎨 **Creative Assistance** - Help with writing, coding, and analysis\n⚡ **Fast Processing** - Optimized for quick responses\n🌐 **Always Available** - Works even with network limitations\n\nHow can I help you today?',

    try {        timestamp: new Date().toISOString(),

      const response = await fetch('http://localhost:8000/conversations');      };

      if (response.ok) {      setMessages([welcomeMessage]);

        const data = await response.json();    }

        setConversations(data);    setStreamingContent('');

      }  }, [conversation]);

    } catch (error) {

      console.error('Failed to fetch conversations:', error);  useEffect(() => {

    }    scrollToBottom();

  };  }, [messages, streamingContent]);



  const createNewConversation = async () => {  useEffect(() => {

    try {    // Auto-resize textarea

      const response = await fetch('http://localhost:8000/conversations', {    if (textareaRef.current) {

        method: 'POST',      textareaRef.current.style.height = '52px';

        headers: { 'Content-Type': 'application/json' },      const scrollHeight = textareaRef.current.scrollHeight;

        body: JSON.stringify({ title: 'New Conversation' })      textareaRef.current.style.height = Math.min(scrollHeight, 120) + 'px';

      });    }

      if (response.ok) {  }, [input]);

        const newConv = await response.json();

        setConversations([newConv, ...conversations]);  const scrollToBottom = () => {

        setCurrentConversationId(newConv.id);    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

        setMessages([]);  };

      }

    } catch (error) {  const handleSubmit = async (e: React.FormEvent) => {

      console.error('Failed to create conversation:', error);    e.preventDefault();

    }    if (!input.trim() || isLoading) return;

  };

    const userMessage = input.trim();

  const scrollToBottom = () => {    setInput('');

    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });    setIsLoading(true);

  };    setIsTyping(true);

    setConnectionStatus('connecting');

  const handleSendMessage = async () => {    setStreamingContent('');

    if (!input.trim() || isLoading) return;

    // Add user message to UI immediately

    const userMessage = input.trim();    const tempUserMessage: Message = {

    setInput('');      id: Date.now(),

    setIsLoading(true);      conversation_id: conversation?.id || 0,

      role: 'user',

    // Add user message immediately      content: userMessage,

    const userMsg: Message = {      timestamp: new Date().toISOString(),

      id: Date.now(),    };

      role: 'user',    setMessages(prev => [...prev, tempUserMessage]);

      content: userMessage,

      timestamp: new Date().toISOString(),    try {

    };      const chatRequest = {

    setMessages(prev => [...prev, userMsg]);        message: userMessage,

        conversation_id: conversation?.id,

    try {        use_search: useSearch,

      // Add streaming message placeholder        conversation_history: messages.map(m => ({

      const streamingMsgId = Date.now() + 1;          role: m.role,

      const streamingMsg: Message = {          content: m.content

        id: streamingMsgId,        }))

        role: 'assistant',      };

        content: '',

        timestamp: new Date().toISOString(),      let fullResponse = '';

        isStreaming: true,      let conversationId = conversation?.id;

      };      setConnectionStatus('connected');

      setMessages(prev => [...prev, streamingMsg]);

      for await (const data of chatService.streamChat(chatRequest)) {

      // Send to backend API        if (data.type === 'conversation_id') {

      const apiResponse = await fetch('http://localhost:8000/api/v1/chat', {          conversationId = data.conversation_id;

        method: 'POST',          if (!conversation) {

        headers: { 'Content-Type': 'application/json' },            // This is a new conversation, we should update the parent

        body: JSON.stringify({ message: userMessage }),            const newConversation: Conversation = {

      });              id: conversationId || 0,

                    title: userMessage.length > 50 ? userMessage.substring(0, 50) + '...' : userMessage,

      if (apiResponse.ok) {              created_at: new Date().toISOString(),

        const data = await apiResponse.json();              updated_at: new Date().toISOString(),

        setMessages(prev =>               messages: [],

          prev.map(msg =>             };

            msg.id === streamingMsgId             onConversationCreated(newConversation);

              ? { ...msg, content: data.message, isStreaming: false }          }

              : msg        } else if (data.type === 'content') {

          )          fullResponse += data.content;

        );          setStreamingContent(fullResponse);

      } else {          setIsTyping(false);

        throw new Error('API request failed');        } else if (data.type === 'done') {

      }          // Add assistant message to messages

    } catch (error) {          const assistantMessage: Message = {

      console.error('Error sending message:', error);            id: Date.now() + 1,

      setMessages(prev =>             conversation_id: conversationId || 0,

        prev.map(msg =>             role: 'assistant',

          msg.id === streamingMsgId             content: fullResponse,

            ? { ...msg, content: 'Sorry, there was an error processing your request. Please try again.', isStreaming: false }            timestamp: new Date().toISOString(),

            : msg          };

        )          setMessages(prev => [...prev, assistantMessage]);

      );          setStreamingContent('');

    } finally {        } else if (data.type === 'error') {

      setIsLoading(false);          console.error('Chat error:', data.error);

    }          setStreamingContent('');

  };          setConnectionStatus('disconnected');

          // Add fallback error message

  const renderMarkdown = (content: string) => {          const errorMessage: Message = {

    return content            id: Date.now() + 2,

      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')            conversation_id: conversationId || 0,

      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')            role: 'assistant',

      .replace(/`(.*?)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono">$1</code>')            content: '⚠️ **Connection Issue Detected**\n\nI\'m experiencing some technical difficulties, but I\'m still here to help! This might be due to:\n\n• Network connectivity issues\n• Server maintenance\n• API limitations\n\n🚀 **Don\'t worry!** I\'m designed to work even with limited connectivity. Please try again in a moment!',

      .replace(/\n/g, '<br>');            timestamp: new Date().toISOString(),

  };          };

          setMessages(prev => [...prev, errorMessage]);

  return (        }

    <div className={`flex h-screen ${darkMode ? 'dark' : ''}`}>      }

      {/* Sidebar */}    } catch (error) {

      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">      console.error('Error sending message:', error);

        <div className="p-4 border-b border-gray-200 dark:border-gray-700">      setStreamingContent('');

          <button      setConnectionStatus('disconnected');

            onClick={createNewConversation}      

            className="w-full flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"      // Enhanced fallback message

          >      const fallbackMessage: Message = {

            <Plus size={16} />        id: Date.now() + 3,

            New Chat        conversation_id: conversation?.id || 0,

          </button>        role: 'assistant',

        </div>        content: `🤖 **AI Assistant Response** (Offline Mode)\n\nI understand you're asking about: "${userMessage}"\n\nWhile I'm experiencing connectivity issues, I can still help you! Here are some suggestions:\n\n• **For coding questions**: I can help with syntax, best practices, and debugging\n• **For writing**: I can assist with structure, grammar, and style\n• **For analysis**: I can provide frameworks and methodologies\n• **For creative tasks**: I can suggest approaches and techniques\n\nPlease try your question again, and I'll do my best to assist you! 🚀`,

                timestamp: new Date().toISOString(),

        <div className="flex-1 overflow-y-auto p-4 space-y-2">      };

          {conversations.map((conversation) => (      setMessages(prev => [...prev, fallbackMessage]);

            <button    } finally {

              key={conversation.id}      setIsLoading(false);

              onClick={() => setCurrentConversationId(conversation.id)}      setIsTyping(false);

              className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${    }

                currentConversationId === conversation.id  };

                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'

                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'  const handleKeyDown = (e: React.KeyboardEvent) => {

              }`}    if (e.key === 'Enter' && !e.shiftKey) {

            >      e.preventDefault();

              <div className="flex items-center gap-2">      handleSubmit(e as any);

                <MessageSquare size={16} />    }

                <span className="truncate text-sm">{conversation.title}</span>  };

              </div>

            </button>  const getConnectionStatusColor = () => {

          ))}    switch (connectionStatus) {

        </div>      case 'connected': return 'text-green-400';

      case 'connecting': return 'text-yellow-400';

        <div className="p-4 border-t border-gray-200 dark:border-gray-700">      case 'disconnected': return 'text-red-400';

          <div className="flex items-center justify-between mb-2">      default: return 'text-gray-400';

            <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>    }

            <button  };

              onClick={() => setDarkMode(!darkMode)}

              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"  const getConnectionIcon = () => {

            >    switch (connectionStatus) {

              {darkMode ? <Sun size={16} /> : <Moon size={16} />}      case 'connected': return <Wifi className="h-3 w-3" />;

            </button>      case 'connecting': return <Activity className="h-3 w-3 animate-pulse" />;

          </div>      case 'disconnected': return <WifiOff className="h-3 w-3" />;

          <div className="flex items-center gap-2 text-xs">      default: return <Wifi className="h-3 w-3" />;

            <div className={`w-2 h-2 rounded-full ${    }

              connectionStatus === 'connected' ? 'bg-green-500' :   };

              connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'

            }`}></div>  return (

            <span className="text-gray-500 dark:text-gray-400">    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative overflow-hidden">

              {connectionStatus === 'connected' ? 'Connected' :       {/* Animated background pattern */}

               connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}      <div className="absolute inset-0 grid-pattern opacity-20"></div>

            </span>      

          </div>      {/* Enhanced Header */}

        </div>      <div className="glass border-b border-gray-700/50 p-4 relative z-10">

      </div>        <div className="flex items-center justify-between">

          <div className="flex items-center space-x-4">

      {/* Main Chat Area */}            <button

      <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">              onClick={onToggleSidebar}

        {/* Header */}              className="enhanced-button p-2 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl transition-all duration-300 hover:scale-105"

        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">            >

          <h1 className="text-xl font-semibold text-gray-800 dark:text-white flex items-center gap-2">              <Menu className="w-5 h-5 text-gray-300" />

            <Bot className="text-blue-600" size={24} />            </button>

            ChatGPT Clone            

            <span className="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">            <div className="flex items-center space-x-3">

              Powered by LLM              <div className="relative">

            </span>                <Bot className="h-8 w-8 text-green-400 floating" />

          </h1>                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full neon-glow"></div>

        </div>              </div>

              <div>

        {/* Messages */}                <h1 className="text-xl font-bold text-white">

        <div className="flex-1 overflow-y-auto p-4 space-y-4">                  {conversation?.title || 'Advanced AI Assistant'}

          {messages.length === 0 ? (                </h1>

            <div className="text-center text-gray-500 dark:text-gray-400 mt-20">                <div className="flex items-center space-x-2 text-sm">

              <Bot size={48} className="mx-auto mb-4 text-blue-600" />                  {getConnectionIcon()}

              <h2 className="text-2xl font-semibold mb-2">Welcome to ChatGPT Clone</h2>                  <span className={getConnectionStatusColor()}>

              <p>Start a conversation by typing a message below</p>                    {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}

            </div>                  </span>

          ) : (                  {useSearch && (

            messages.map((message) => (                    <div className="flex items-center space-x-1 text-green-400">

              <div                      <Globe className="h-3 w-3" />

                key={message.id}                      <span>Web Search Active</span>

                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}                    </div>

              >                  )}

                <div className={`flex gap-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>                </div>

                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${              </div>

                    message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'            </div>

                  }`}>          </div>

                    {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}          

                  </div>          <div className="flex items-center space-x-2">

                  <div className={`px-4 py-3 rounded-xl ${            <button

                    message.role === 'user'              onClick={() => setUseSearch(!useSearch)}

                      ? 'bg-blue-600 text-white'              className={`enhanced-button px-4 py-2 rounded-xl border transition-all duration-300 ${

                      : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-white border border-gray-200 dark:border-gray-600 shadow-sm'                useSearch

                  }`}>                  ? 'bg-green-500/20 border-green-400 text-green-400 shadow-glow'

                    <div                   : 'bg-gray-700/50 border-gray-600 text-gray-300 hover:bg-gray-600/50'

                      dangerouslySetInnerHTML={{               }`}

                        __html: message.role === 'assistant' ? renderMarkdown(message.content) : message.content             >

                      }}               <div className="flex items-center space-x-2">

                      className="prose prose-sm max-w-none dark:prose-invert"                {useSearch ? <Globe className="h-4 w-4" /> : <Search className="h-4 w-4" />}

                    />                <span className="hidden sm:inline">Web Search</span>

                    {message.isStreaming && (              </div>

                      <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />            </button>

                    )}          </div>

                  </div>        </div>

                </div>      </div>

              </div>

            ))      {/* Enhanced Messages Area */}

          )}      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">

          <div ref={messagesEndRef} />        {messages.length === 0 && !streamingContent && (

        </div>          <div className="flex items-center justify-center h-full">

            <div className="text-center space-y-6 message-bubble">

        {/* Input Area */}              <div className="relative">

        <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">                <Bot className="w-16 h-16 mx-auto text-green-400 floating" />

          <div className="flex gap-3">                <Sparkles className="w-6 h-6 absolute -top-2 -right-2 text-yellow-400 animate-pulse" />

            <input              </div>

              ref={inputRef}              <div className="space-y-3">

              type="text"                <h2 className="text-3xl font-bold text-white">How can I help you today?</h2>

              value={input}                <p className="text-gray-400 text-lg">Start a conversation by typing a message below.</p>

              onChange={(e) => setInput(e.target.value)}                <div className="flex flex-wrap justify-center gap-2 mt-6">

              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}                  <div className="modern-card px-4 py-2 bg-green-500/10 border border-green-400/30 text-green-400 text-sm">

              placeholder="Type your message..."                    💬 Natural Conversations

              disabled={isLoading}                  </div>

              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-none"                  <div className="modern-card px-4 py-2 bg-blue-500/10 border border-blue-400/30 text-blue-400 text-sm">

            />                    🔍 Web Search

            <button                  </div>

              onClick={handleSendMessage}                  <div className="modern-card px-4 py-2 bg-purple-500/10 border border-purple-400/30 text-purple-400 text-sm">

              disabled={!input.trim() || isLoading}                    🎨 Creative Tasks

              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium"                  </div>

            >                  <div className="modern-card px-4 py-2 bg-orange-500/10 border border-orange-400/30 text-orange-400 text-sm">

              {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}                    ⚡ Fast Responses

              Send                  </div>

            </button>                </div>

          </div>              </div>

        </div>            </div>

      </div>          </div>

    </div>        )}

  );

};        {messages.map((message) => (

          <MessageBubble key={message.id} message={message} />

export default ChatInterface;        ))}

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