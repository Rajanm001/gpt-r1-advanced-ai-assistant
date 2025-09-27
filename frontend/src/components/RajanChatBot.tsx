'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Plus, Search, Github, Globe, Lightbulb, Coffee, Code, Brain, Sparkles, Zap } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Suggestion {
  icon: React.ReactNode;
  title: string;
  description: string;
  prompt: string;
}

const RajanChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const suggestions: Suggestion[] = [
    {
      icon: <Code className="w-5 h-5" />,
      title: "Write Code",
      description: "Create functions, classes, or complete applications",
      prompt: "Help me write a Python function that"
    },
    {
      icon: <Brain className="w-5 h-5" />,
      title: "Deep Research",
      description: "Get comprehensive analysis on any topic",
      prompt: "Provide deep research and analysis on"
    },
    {
      icon: <Search className="w-5 h-5" />,
      title: "Advanced Search",
      description: "Find detailed information with citations",
      prompt: "Search and analyze the latest information about"
    },
    {
      icon: <Lightbulb className="w-5 h-5" />,
      title: "Creative Ideas",
      description: "Brainstorm innovative solutions",
      prompt: "Give me creative ideas for"
    },
    {
      icon: <Zap className="w-5 h-5" />,
      title: "Quick Solutions",
      description: "Fast answers to technical problems",
      prompt: "Solve this problem quickly:"
    },
    {
      icon: <Sparkles className="w-5 h-5" />,
      title: "Advanced Features",
      description: "Explore complex AI capabilities",
      prompt: "Show me advanced techniques for"
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message from Rajan Bot
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: '1',
        role: 'assistant',
        content: `🤖 **Hey! I am Rajan Bot** - Your Advanced AI Assistant!

Welcome to the most powerful ChatGPT clone! I'm here to help you with:

✨ **Advanced Features:**
- 🧠 Deep research and analysis
- 💻 Code generation and debugging  
- 🔍 Comprehensive search capabilities
- 💡 Creative problem solving
- ⚡ Lightning-fast responses
- 🌐 Real-time information

I'm always online and ready to provide the best answers to all your questions. What would you like to explore today?`,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, []);

  const sendMessage = async (messageContent?: string) => {
    const content = messageContent || inputMessage.trim();
    if (!content) return;

    setInputMessage('');
    setShowSuggestions(false);
    setIsLoading(true);
    setIsTyping(true);

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
          conversation_history: []
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      let assistantContent = '';
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'content') {
                assistantContent += parsed.content;
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === assistantMessage.id 
                      ? { ...msg, content: assistantContent }
                      : msg
                  )
                );
              } else if (parsed.type === 'conversation_id') {
                setConversationId(parsed.conversation_id);
              }
            } catch (e) {
              // Ignore JSON parse errors for non-JSON data
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: `🔧 **Rajan Bot is temporarily offline but still working!**

I apologize for the connection issue. As your advanced AI assistant, I can still help you with:

• **Code Development**: Write, debug, and optimize code
• **Research & Analysis**: Deep dive into any topic
• **Problem Solving**: Creative and technical solutions
• **Learning Support**: Explanations and tutorials

Please try your question again, and I'll provide the best assistance possible!`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setShowSuggestions(true);
    setInputMessage('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Advanced Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-700"></div>
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-green-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto h-screen flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between p-4 border-b border-gray-700/50 backdrop-blur-xl bg-gray-900/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Rajan Bot
              </h1>
              <p className="text-sm text-gray-400">Advanced AI Assistant • Always Online</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={startNewChat}
              className="p-2 rounded-lg bg-gray-700/50 hover:bg-gray-600/50 transition-all duration-200 backdrop-blur-sm"
              title="New Chat"
            >
              <Plus className="w-5 h-5" />
            </button>
            <a
              href="https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg bg-gray-700/50 hover:bg-gray-600/50 transition-all duration-200 backdrop-blur-sm"
              title="GitHub Repository"
            >
              <Github className="w-5 h-5" />
            </a>
            <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-green-500/20 border border-green-500/30">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-400 font-medium">Online</span>
            </div>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {showSuggestions && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => sendMessage(suggestion.prompt)}
                  className="p-4 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700/50 hover:border-gray-600/50 transition-all duration-300 text-left group backdrop-blur-sm"
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500/20 to-purple-500/20 group-hover:from-blue-500/30 group-hover:to-purple-500/30 transition-all duration-300">
                      {suggestion.icon}
                    </div>
                    <h3 className="font-semibold text-white">{suggestion.title}</h3>
                  </div>
                  <p className="text-gray-400 text-sm">{suggestion.description}</p>
                </button>
              ))}
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-4xl flex ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                } space-x-3`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-green-500 to-emerald-600'
                      : 'bg-gradient-to-r from-blue-500 to-purple-600'
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="w-6 h-6 text-white" />
                  ) : (
                    <Bot className="w-6 h-6 text-white" />
                  )}
                </div>
                <div
                  className={`p-4 rounded-2xl backdrop-blur-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30'
                      : 'bg-gray-800/50 border border-gray-700/50'
                  }`}
                >
                  <div className="prose prose-invert max-w-none">
                    <div
                      className="text-white leading-relaxed whitespace-pre-wrap"
                      dangerouslySetInnerHTML={{
                        __html: message.content
                          .replace(/\*\*(.*?)\*\*/g, '<strong class="text-blue-400">$1</strong>')
                          .replace(/\*(.*?)\*/g, '<em class="text-purple-400">$1</em>')
                          .replace(/`(.*?)`/g, '<code class="bg-gray-700/50 px-2 py-1 rounded text-green-400">$1</code>')
                          .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-900/50 p-4 rounded-lg border border-gray-700/50 overflow-x-auto"><code class="text-green-400">$1</code></pre>')
                      }}
                    />
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="max-w-4xl flex flex-row space-x-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div className="p-4 rounded-2xl bg-gray-800/50 border border-gray-700/50 backdrop-blur-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700/50 backdrop-blur-xl bg-gray-900/50">
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Rajan Bot anything... I'm here to help with coding, research, and more!"
                className="w-full p-4 pr-12 rounded-xl bg-gray-800/50 border border-gray-700/50 focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 resize-none transition-all duration-200 backdrop-blur-sm text-white placeholder-gray-400"
                rows={3}
                disabled={isLoading}
              />
              <div className="absolute right-3 bottom-3 flex space-x-2">
                <button
                  onClick={() => sendMessage()}
                  disabled={!inputMessage.trim() || isLoading}
                  className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg"
                >
                  <Send className="w-5 h-5 text-white" />
                </button>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4" />
                <span>Always Online</span>
              </div>
              <div className="flex items-center space-x-2">
                <Coffee className="w-4 h-4" />
                <span>Powered by Advanced AI</span>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RajanChatBot;