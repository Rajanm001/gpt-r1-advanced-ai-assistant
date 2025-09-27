'use client';'use client';'use client';'use client';



import { useState, useRef, useEffect } from 'react';

import { Send, Plus, Bot, User, Palette } from 'lucide-react';

import { useState, useRef, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

import { Send, Plus, Bot, User, Palette } from 'lucide-react';

const themes = {

  blue: { primary: '#3b82f6', secondary: '#1d4ed8', accent: '#60a5fa', name: 'Ocean Blue' },import { useState, useRef, useEffect } from 'react';import { useState, useRef, useEffect } from 'react';

  purple: { primary: '#8b5cf6', secondary: '#7c3aed', accent: '#a78bfa', name: 'Royal Purple' },

  green: { primary: '#10b981', secondary: '#059669', accent: '#34d399', name: 'Emerald Green' },const API_BASE = 'http://localhost:8000/api/v1';

  orange: { primary: '#f59e0b', secondary: '#d97706', accent: '#fbbf24', name: 'Sunset Orange' },

  red: { primary: '#ef4444', secondary: '#dc2626', accent: '#f87171', name: 'Ruby Red' }import { Send, Plus, Bot, User, Palette } from 'lucide-react';import { Send, Plus, Bot, User, Palette, Settings } from 'lucide-react';

};

const themes = {

interface Message {

  id: string;  blue: { primary: '#3b82f6', secondary: '#1d4ed8', accent: '#60a5fa', name: 'Ocean Blue' },

  role: 'user' | 'assistant';

  content: string;  purple: { primary: '#8b5cf6', secondary: '#7c3aed', accent: '#a78bfa', name: 'Royal Purple' },

  timestamp: string;

}  green: { primary: '#10b981', secondary: '#059669', accent: '#34d399', name: 'Emerald Green' },const API_BASE = 'http://localhost:8000/api/v1';const API_BASE = 'http://localhost:8000/api/v1';



interface Conversation {  orange: { primary: '#f59e0b', secondary: '#d97706', accent: '#fbbf24', name: 'Sunset Orange' },

  id: string;

  title: string;  red: { primary: '#ef4444', secondary: '#dc2626', accent: '#f87171', name: 'Ruby Red' }

  created_at: string;

  message_count: number;};

}

// Theme configurations// Theme configurations

export default function ChatGPTClone() {

  const [messages, setMessages] = useState<Message[]>([]);interface Message {

  const [inputText, setInputText] = useState('');

  const [isLoading, setIsLoading] = useState(false);  id: string;const themes = {const themes = {

  const [conversations, setConversations] = useState<Conversation[]>([]);

  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);  role: 'user' | 'assistant';

  const [streamingContent, setStreamingContent] = useState('');

  const [error, setError] = useState('');  content: string;  blue: {  blue: {

  const [isConnected, setIsConnected] = useState(false);

  const [currentTheme, setCurrentTheme] = useState('blue');  timestamp: string;

  

  const messagesEndRef = useRef<HTMLDivElement>(null);}    primary: '#3b82f6',    primary: '#3b82f6',

  const textareaRef = useRef<HTMLTextAreaElement>(null);



  const scrollToBottom = () => {

    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });interface Conversation {    secondary: '#1d4ed8',    secondary: '#1d4ed8',

  };

  id: string;

  useEffect(() => {

    scrollToBottom();  title: string;    accent: '#60a5fa',    accent: '#60a5fa',

  }, [messages, streamingContent]);

  created_at: string;

  useEffect(() => {

    if (textareaRef.current) {  message_count: number;    name: 'Ocean Blue'    name: 'Ocean Blue'

      textareaRef.current.style.height = 'auto';

      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;}

    }

  }, [inputText]);  },  },



  const loadConversations = async () => {export default function ModernChatGPT() {

    try {

      const response = await fetch(`${API_BASE}/conversations`);  const [messages, setMessages] = useState<Message[]>([]);  purple: {  purple: {

      if (response.ok) {

        const data = await response.json();  const [inputText, setInputText] = useState('');

        setConversations(data.conversations || []);

        setIsConnected(true);  const [isLoading, setIsLoading] = useState(false);    primary: '#8b5cf6',    primary: '#8b5cf6',

        setError('');

      } else {  const [conversations, setConversations] = useState<Conversation[]>([]);

        setError('Failed to connect to server');

        setIsConnected(false);  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);    secondary: '#7c3aed',    secondary: '#7c3aed',

      }

    } catch (error) {  const [streamingContent, setStreamingContent] = useState('');

      console.error('Connection error:', error);

      setError('Server not reachable');  const [error, setError] = useState('');    accent: '#a78bfa',    accent: '#a78bfa',

      setIsConnected(false);

    }  const [isConnected, setIsConnected] = useState(false);

  };

  const [currentTheme, setCurrentTheme] = useState('blue');    name: 'Royal Purple'    name: 'Royal Purple'

  const createNewConversation = async () => {

    try {  

      const response = await fetch(`${API_BASE}/conversations`, {

        method: 'POST',  const messagesEndRef = useRef<HTMLDivElement>(null);  },  },

        headers: { 'Content-Type': 'application/json' },

        body: JSON.stringify({ title: 'New Chat' }),  const textareaRef = useRef<HTMLTextAreaElement>(null);

      });

        green: {  green: {

      if (response.ok) {

        const newConversation = await response.json();  const scrollToBottom = () => {

        setCurrentConversationId(newConversation.id);

        setMessages([]);    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });    primary: '#10b981',    primary: '#10b981',

        setStreamingContent('');

        setError('');  };

        loadConversations();

      }    secondary: '#059669',    secondary: '#059669',

    } catch (error) {

      console.error('Failed to create conversation:', error);  useEffect(() => {

      setError('Failed to create new conversation');

    }    scrollToBottom();    accent: '#34d399',    accent: '#34d399',

  };

  }, [messages, streamingContent]);

  const sendMessage = async () => {

    if (!inputText.trim() || isLoading) return;    name: 'Emerald Green'    name: 'Emerald Green'

    

    setError('');  useEffect(() => {

    const userMessage = inputText.trim();

    setInputText('');    if (textareaRef.current) {  },  },

    setIsLoading(true);

    setStreamingContent('');      textareaRef.current.style.height = 'auto';



    const userMsg: Message = {      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;  orange: {  orange: {

      id: Date.now().toString(),

      role: 'user',    }

      content: userMessage,

      timestamp: new Date().toISOString()  }, [inputText]);    primary: '#f59e0b',    primary: '#f59e0b',

    };

    

    setMessages(prev => [...prev, userMsg]);

  const loadConversations = async () => {    secondary: '#d97706',    secondary: '#d97706',

    try {

      const response = await fetch(`${API_BASE}/chat`, {    try {

        method: 'POST',

        headers: { 'Content-Type': 'application/json' },      const response = await fetch(`${API_BASE}/conversations`);    accent: '#fbbf24',    accent: '#fbbf24',

        body: JSON.stringify({

          message: userMessage,      if (response.ok) {

          conversation_id: currentConversationId

        }),        const data = await response.json();    name: 'Sunset Orange'    name: 'Sunset Orange'

      });

        setConversations(data.conversations || []);

      if (!response.ok) {

        throw new Error(`Server error: ${response.status}`);        setIsConnected(true);  },  },

      }

        setError('');

      const reader = response.body?.getReader();

      if (!reader) throw new Error('No response stream');      } else {  red: {  red: {



      let fullResponse = '';        setError('Failed to connect to server');

      let conversationId = currentConversationId;

        setIsConnected(false);    primary: '#ef4444',    primary: '#ef4444',

      while (true) {

        const { done, value } = await reader.read();      }

        if (done) break;

    } catch (error) {    secondary: '#dc2626',    secondary: '#dc2626',

        const chunk = new TextDecoder().decode(value);

        const lines = chunk.split('\n');      console.error('Connection error:', error);



        for (const line of lines) {      setError('Server not reachable');    accent: '#f87171',    accent: '#f87171',

          if (line.startsWith('data: ')) {

            const data = line.slice(6);      setIsConnected(false);

            if (data.trim() === '[DONE]') continue;

    }    name: 'Ruby Red'    name: 'Ruby Red'

            try {

              const parsed = JSON.parse(data);  };

              

              if (parsed.error) {  }  },

                setError(parsed.error);

                continue;  const createNewConversation = async () => {

              }

                  try {};  dark: {

              if (parsed.conversation_id && !currentConversationId) {

                conversationId = parsed.conversation_id;      const response = await fetch(`${API_BASE}/conversations`, {

                setCurrentConversationId(conversationId);

              }        method: 'POST',    primary: '#6b7280',

              

              if (parsed.content) {        headers: { 'Content-Type': 'application/json' },

                fullResponse += parsed.content;

                setStreamingContent(fullResponse);        body: JSON.stringify({ title: 'New Chat' }),interface Message {    secondary: '#4b5563',

              }

                    });

              if (parsed.done) {

                const assistantMsg: Message = {        id: string;    accent: '#9ca3af',

                  id: (Date.now() + 1).toString(),

                  role: 'assistant',      if (response.ok) {

                  content: fullResponse,

                  timestamp: new Date().toISOString()        const newConversation = await response.json();  role: 'user' | 'assistant';    name: 'Dark Matter'

                };

                        setCurrentConversationId(newConversation.id);

                setMessages(prev => [...prev, assistantMsg]);

                setStreamingContent('');        setMessages([]);  content: string;  }

                loadConversations();

                break;        setStreamingContent('');

              }

            } catch (parseError) {        setError('');  timestamp: string;};

              console.error('Parse error:', parseError);

            }        loadConversations();

          }

        }      }}

      }

    } catch (error) {    } catch (error) {

      console.error('Chat error:', error);

      setError(error instanceof Error ? error.message : 'Failed to send message');      console.error('Failed to create conversation:', error);interface Message {

    } finally {

      setIsLoading(false);      setError('Failed to create new conversation');

      setStreamingContent('');

    }    }interface Conversation {  id: string;

  };

  };

  useEffect(() => {

    loadConversations();  id: string;  role: 'user' | 'assistant';

  }, []);

  const sendMessage = async () => {

  const handleKeyPress = (e: React.KeyboardEvent) => {

    if (e.key === 'Enter' && !e.shiftKey) {    if (!inputText.trim() || isLoading) return;  title: string;  content: string;

      e.preventDefault();

      sendMessage();    

    }

  };    setError('');  created_at: string;  timestamp: string;



  const changeTheme = (themeKey: string) => {    const userMessage = inputText.trim();

    setCurrentTheme(themeKey);

  };    setInputText('');  message_count: number;}



  const currentThemeColors = themes[currentTheme as keyof typeof themes];    setIsLoading(true);



  return (    setStreamingContent('');}

    <div className="flex h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white font-inter">

      <div className="w-80 bg-gray-800/50 backdrop-blur-xl border-r border-gray-700/50 flex flex-col">

        <div className="p-6 border-b border-gray-700/50">

          <button    const userMsg: Message = {interface Conversation {

            onClick={createNewConversation}

            style={{       id: Date.now().toString(),

              background: `linear-gradient(135deg, ${currentThemeColors.primary}, ${currentThemeColors.secondary})` 

            }}      role: 'user',export default function ModernChatGPT() {  id: string;

            className="w-full flex items-center gap-3 px-4 py-3 text-white rounded-xl font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg"

          >      content: userMessage,

            <Plus size={20} />

            New Chat      timestamp: new Date().toISOString()  // State management  title: string;

          </button>

              };

          <div className="mt-4 flex items-center gap-2 text-sm text-gray-400">

            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>      const [messages, setMessages] = useState<Message[]>([]);  created_at: string;

            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>

          </div>    setMessages(prev => [...prev, userMsg]);

        </div>

  const [inputText, setInputText] = useState('');  message_count: number;

        <div className="flex-1 overflow-y-auto p-4 space-y-2">

          <h3 className="text-sm font-semibold text-gray-400 mb-3">Recent Conversations</h3>    try {

          

          {conversations.length === 0 ? (      const response = await fetch(`${API_BASE}/chat`, {  const [isLoading, setIsLoading] = useState(false);}

            <div className="text-center py-8 text-gray-500">

              <Bot size={32} className="mx-auto mb-2 opacity-50" />        method: 'POST',

              <p className="text-sm">No conversations yet</p>

            </div>        headers: { 'Content-Type': 'application/json' },  const [conversations, setConversations] = useState<Conversation[]>([]);

          ) : (

            conversations.map((conv) => (        body: JSON.stringify({

              <button

                key={conv.id}          message: userMessage,  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);export default function ModernChatGPT() {

                onClick={() => {

                  setCurrentConversationId(conv.id);          conversation_id: currentConversationId

                  setMessages([]);

                  setStreamingContent('');        }),  const [streamingContent, setStreamingContent] = useState('');  // State management

                }}

                className={`w-full text-left p-3 rounded-lg transition-all duration-200 hover:bg-gray-700/50 ${      });

                  currentConversationId === conv.id 

                    ? 'bg-gray-700/70 border border-gray-600'   const [error, setError] = useState('');  const [messages, setMessages] = useState<Message[]>([]);

                    : 'border border-transparent'

                }`}      if (!response.ok) {

              >

                <div className="flex items-start gap-2">        throw new Error(`Server error: ${response.status}`);  const [isConnected, setIsConnected] = useState(false);  const [inputText, setInputText] = useState('');

                  <Bot size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />

                  <div className="min-w-0 flex-1">      }

                    <p className="text-sm font-medium text-gray-200 truncate">

                      {conv.title}  const [currentTheme, setCurrentTheme] = useState('blue');  const [isLoading, setIsLoading] = useState(false);

                    </p>

                    <p className="text-xs text-gray-500 mt-1">      const reader = response.body?.getReader();

                      {conv.message_count} messages

                    </p>      if (!reader) throw new Error('No response stream');    const [conversations, setConversations] = useState<Conversation[]>([]);

                  </div>

                </div>

              </button>

            ))      let fullResponse = '';  const messagesEndRef = useRef<HTMLDivElement>(null);  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

          )}

        </div>      let conversationId = currentConversationId;



        <div className="p-4 border-t border-gray-700/50">  const textareaRef = useRef<HTMLTextAreaElement>(null);  const [streamingContent, setStreamingContent] = useState('');

          <div className="flex items-center gap-2 mb-3">

            <Palette size={16} className="text-gray-400" />      while (true) {

            <span className="text-sm font-medium text-gray-300">Themes</span>

          </div>        const { done, value } = await reader.read();  const [error, setError] = useState('');

          <div className="grid grid-cols-3 gap-2">

            {Object.entries(themes).map(([key, theme]) => (        if (done) break;

              <button

                key={key}  // Auto scroll to bottom  const [isConnected, setIsConnected] = useState(false);

                onClick={() => changeTheme(key)}

                className={`w-10 h-10 rounded-lg transition-all duration-200 hover:scale-110 ${        const chunk = new TextDecoder().decode(value);

                  currentTheme === key ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-800' : ''

                }`}        const lines = chunk.split('\n');  const scrollToBottom = () => {  const [currentTheme, setCurrentTheme] = useState('blue');

                style={{ background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})` }}

                title={theme.name}

              />

            ))}        for (const line of lines) {    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });  const [sidebarOpen, setSidebarOpen] = useState(false);

          </div>

        </div>          if (line.startsWith('data: ')) {

      </div>

            const data = line.slice(6);  };  

      <div className="flex-1 flex flex-col">

        <div className="p-6 bg-gray-800/30 backdrop-blur-xl border-b border-gray-700/50">            if (data.trim() === '[DONE]') continue;

          <div className="flex items-center gap-3">

            <div   const messagesEndRef = useRef<HTMLDivElement>(null);

              className="w-12 h-12 rounded-xl flex items-center justify-center text-white"

              style={{ background: `linear-gradient(135deg, ${currentThemeColors.primary}, ${currentThemeColors.secondary})` }}            try {

            >

              <Bot size={24} />              const parsed = JSON.parse(data);  useEffect(() => {  const textareaRef = useRef<HTMLTextAreaElement>(null);

            </div>

            <div>              

              <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">

                Advanced AI Assistant              if (parsed.error) {    scrollToBottom();

              </h1>

              <p className="text-sm text-gray-400">                setError(parsed.error);

                Powered by OpenRouter • WizardLM-2-8x22B • {isConnected ? '🟢 Online' : '🔴 Offline'}

              </p>                continue;  }, [messages, streamingContent]);    

            </div>

          </div>              }

        </div>

              

        <div className="flex-1 overflow-y-auto">

          {messages.length === 0 && !streamingContent ? (              if (parsed.conversation_id) {

            <div className="flex items-center justify-center h-full">

              <div className="text-center max-w-md">                conversationId = parsed.conversation_id;  // Auto-resize textarea    setMessages(prev => [...prev, userMsg]);  const [streaming, setStreaming] = useState('');

                <div 

                  className="w-20 h-20 rounded-2xl flex items-center justify-center text-white mb-6 mx-auto animate-pulse"                if (!currentConversationId) {

                  style={{ background: `linear-gradient(135deg, ${currentThemeColors.primary}, ${currentThemeColors.secondary})` }}

                >                  setCurrentConversationId(conversationId);  useEffect(() => {

                  <Bot size={40} />

                </div>                }

                <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-4">

                  Welcome to Advanced AI              }    if (textareaRef.current) {

                </h2>

                <p className="text-gray-400 text-lg">              

                  Start a conversation with our powerful AI assistant!

                </p>              if (parsed.content) {      textareaRef.current.style.height = 'auto';

              </div>

            </div>                fullResponse += parsed.content;

          ) : (

            <div className="space-y-6 p-6">                setStreamingContent(fullResponse);      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;    try {  const [error, setError] = useState('');

              {messages.map((message) => (

                <div              }

                  key={message.id}

                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}                  }

                >

                  <div               if (parsed.done) {

                    className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${

                      message.role === 'user'                 const assistantMsg: Message = {  }, [inputText]);      const res = await fetch('http://localhost:8000/api/v1/chat', {

                        ? 'text-white' 

                        : 'bg-gray-700 text-gray-300'                  id: (Date.now() + 1).toString(),

                    }`}

                    style={message.role === 'user' ? {                   role: 'assistant',

                      background: `linear-gradient(135deg, ${currentThemeColors.primary}, ${currentThemeColors.secondary})` 

                    } : {}}                  content: fullResponse,

                  >

                    {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}                  timestamp: new Date().toISOString()  // Load conversations        method: 'POST',  const [connected, setConnected] = useState(false);

                  </div>

                                  };

                  <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>

                    <div                   const loadConversations = async () => {

                      className={`inline-block p-4 rounded-2xl ${

                        message.role === 'user'                setMessages(prev => [...prev, assistantMsg]);

                          ? 'text-white'

                          : 'bg-gray-800/50 border border-gray-700/50'                setStreamingContent('');    try {        headers: { 'Content-Type': 'application/json' },

                      }`}

                      style={message.role === 'user' ? {                 loadConversations();

                        background: `linear-gradient(135deg, ${currentThemeColors.primary}, ${currentThemeColors.secondary})` 

                      } : {}}                break;      const response = await fetch(`${API_BASE}/conversations`);

                    >

                      <p className="whitespace-pre-wrap m-0">{message.content}</p>              }

                    </div>

                  </div>            } catch (parseError) {      if (response.ok) {        body: JSON.stringify({ message: msg }),  const API_BASE = 'http://localhost:8000/api/v1';import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

                </div>

              ))}              console.error('Parse error:', parseError);



              {streamingContent && (            }        const data = await response.json();

                <div className="flex gap-4">

                  <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-700 flex items-center justify-center">          }

                    <Bot size={20} className="text-gray-300" />

                  </div>        }        setConversations(data.conversations || []);      });

                  <div className="flex-1 max-w-3xl">

                    <div className="inline-block p-4 rounded-2xl bg-gray-800/50 border border-gray-700/50">      }

                      <div className="whitespace-pre-wrap">{streamingContent}</div>

                      <div className="mt-3 flex items-center gap-2 text-blue-400">    } catch (error) {        setIsConnected(true);

                        <div className="flex gap-1">

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>      console.error('Chat error:', error);

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>      setError(error instanceof Error ? error.message : 'Failed to send message');        setError('');  const endRef = useRef(null);

                        </div>

                        <span className="text-sm font-medium">AI is thinking...</span>    } finally {

                      </div>

                    </div>      setIsLoading(false);      } else {

                  </div>

                </div>      setStreamingContent('');

              )}

    }        setError('Failed to connect to server');      if (res.ok) {

              <div ref={messagesEndRef} />

            </div>  };

          )}

        </div>        setIsConnected(false);



        {error && (  useEffect(() => {

          <div className="mx-6 mb-4 bg-red-900/20 border border-red-800/50 text-red-300 px-4 py-3 rounded-xl">

            <span className="text-sm font-medium">Error: {error}</span>    loadConversations();      }        const reader = res.body?.getReader();

          </div>

        )}  }, []);



        <div className="p-6 bg-gray-800/30 backdrop-blur-xl border-t border-gray-700/50">    } catch (error) {

          <div className="flex gap-4 max-w-4xl mx-auto">

            <div className="flex-1 relative">  const handleKeyPress = (e: React.KeyboardEvent) => {

              <textarea

                ref={textareaRef}    if (e.key === 'Enter' && !e.shiftKey) {      console.error('Connection error:', error);        let fullResponse = '';

                value={inputText}

                onChange={(e) => setInputText(e.target.value)}      e.preventDefault();

                onKeyDown={handleKeyPress}

                placeholder="Message Advanced AI Assistant..."      sendMessage();      setError('Server not reachable');

                disabled={isLoading || !isConnected}

                className="w-full resize-none bg-gray-800/50 border border-gray-700/50 rounded-2xl px-6 py-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 disabled:opacity-50"    }

                style={{ 

                  minHeight: '56px',  };      setIsConnected(false);  const scroll = () => endRef.current?.scrollIntoView({ behavior: 'smooth' });

                  maxHeight: '200px'

                }}

                rows={1}

              />  const changeTheme = (themeKey: string) => {    }

            </div>

            <button    setCurrentTheme(themeKey);

              onClick={sendMessage}

              disabled={!inputText.trim() || isLoading || !isConnected}    const theme = themes[themeKey as keyof typeof themes];  };        while (true) {

              className="w-14 h-14 rounded-2xl text-white transition-all duration-300 hover:scale-105 disabled:opacity-50 flex items-center justify-center"

              style={{ background: `linear-gradient(135deg, ${currentThemeColors.primary}, ${currentThemeColors.secondary})` }}    document.documentElement.style.setProperty('--primary-color', theme.primary);

            >

              {isLoading ? (    document.documentElement.style.setProperty('--secondary-color', theme.secondary);

                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />

              ) : (    document.documentElement.style.setProperty('--accent-color', theme.accent);

                <Send size={20} />

              )}  };  // Create new conversation          const { done, value } = await reader.read();  interface Message {import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

            </button>

          </div>

        </div>

      </div>  return (  const createNewConversation = async () => {

    </div>

  );    <div className="flex h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white font-inter">

}
      {/* Sidebar */}    try {          if (done) break;

      <div className="w-80 bg-gray-800/50 backdrop-blur-xl border-r border-gray-700/50 flex flex-col">

        <div className="p-6 border-b border-gray-700/50">      const response = await fetch(`${API_BASE}/conversations`, {

          <button

            onClick={createNewConversation}        method: 'POST',  useEffect(() => scroll(), [messages, streaming]);

            style={{ 

              background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`         headers: { 'Content-Type': 'application/json' },

            }}

            className="w-full flex items-center gap-3 px-4 py-3 text-white rounded-xl font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg"        body: JSON.stringify({ title: 'New Chat' }),          const chunk = new TextDecoder().decode(value);

          >

            <Plus size={20} />      });

            New Chat

          </button>                const lines = chunk.split('\n');  id: string;

          

          <div className="mt-4 flex items-center gap-2 text-sm text-gray-400">      if (response.ok) {

            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>

            <span>{isConnected ? 'Connected to AI' : 'Connection Lost'}</span>        const newConversation = await response.json();

          </div>

        </div>        setCurrentConversationId(newConversation.id);



        <div className="flex-1 overflow-y-auto p-4 space-y-2">        setMessages([]);          for (const line of lines) {  const loadConvs = async () => {

          <h3 className="text-sm font-semibold text-gray-400 mb-3">Recent Conversations</h3>

                  setStreamingContent('');

          {conversations.length === 0 ? (

            <div className="text-center py-8 text-gray-500">        setError('');            if (line.startsWith('data: ')) {

              <Bot size={32} className="mx-auto mb-2 opacity-50" />

              <p className="text-sm">No conversations yet</p>        loadConversations();

              <p className="text-xs mt-1">Start a new chat to begin</p>

            </div>      }              const data = line.slice(6);    try {  role: 'user' | 'assistant';import { Send, MessageSquare, Plus, Bot, User } from 'lucide-react';import { Send, MessageSquare, Plus } from 'lucide-react';

          ) : (

            conversations.map((conv) => (    } catch (error) {

              <button

                key={conv.id}      console.error('Failed to create conversation:', error);              try {

                onClick={() => {

                  setCurrentConversationId(conv.id);      setError('Failed to create new conversation');

                  setMessages([]);

                  setStreamingContent('');    }                const parsed = JSON.parse(data);      const res = await fetch(`${API_BASE}/conversations`);

                }}

                className={`w-full text-left p-3 rounded-lg transition-all duration-200 hover:bg-gray-700/50 ${  };

                  currentConversationId === conv.id 

                    ? 'bg-gray-700/70 border border-gray-600'                 if (parsed.content) {

                    : 'border border-transparent'

                }`}  // Send message with streaming

              >

                <div className="flex items-start gap-2">  const sendMessage = async () => {                  fullResponse += parsed.content;      if (res.ok) {  content: string;

                  <Bot size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />

                  <div className="min-w-0 flex-1">    if (!inputText.trim() || isLoading) return;

                    <p className="text-sm font-medium text-gray-200 truncate">

                      {conv.title}                    }

                    </p>

                    <p className="text-xs text-gray-500 mt-1">    setError('');

                      {conv.message_count} messages • {new Date(conv.created_at).toLocaleDateString()}

                    </p>    const userMessage = inputText.trim();                if (parsed.done) {        const data = await res.json();

                  </div>

                </div>    setInputText('');

              </button>

            ))    setIsLoading(true);                  const aiMsg = {

          )}

        </div>    setStreamingContent('');



        <div className="p-4 border-t border-gray-700/50">                    id: (Date.now() + 1).toString(),        setConversations(data.conversations || []);  timestamp: string;

          <div className="flex items-center gap-2 mb-3">

            <Palette size={16} className="text-gray-400" />    // Add user message immediately

            <span className="text-sm font-medium text-gray-300">Themes</span>

          </div>    const userMsg: Message = {                    role: 'assistant',

          <div className="grid grid-cols-3 gap-2">

            {Object.entries(themes).map(([key, theme]) => (      id: Date.now().toString(),

              <button

                key={key}      role: 'user',                    content: fullResponse        setConnected(true);

                onClick={() => changeTheme(key)}

                className={`w-10 h-10 rounded-lg transition-all duration-200 hover:scale-110 ${      content: userMessage,

                  currentTheme === key ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-800' : ''

                }`}      timestamp: new Date().toISOString()                  };

                style={{ background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})` }}

                title={theme.name}    };

              />

            ))}                      setMessages(prev => [...prev, aiMsg]);        setError('');}

          </div>

        </div>    setMessages(prev => [...prev, userMsg]);

      </div>

                  break;

      {/* Main Chat Area */}

      <div className="flex-1 flex flex-col">    try {

        <div className="p-6 bg-gray-800/30 backdrop-blur-xl border-b border-gray-700/50">

          <div className="flex items-center gap-3">      const response = await fetch(`${API_BASE}/chat`, {                }      } else {

            <div 

              className="w-12 h-12 rounded-xl flex items-center justify-center text-white"        method: 'POST',

              style={{ 

                background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`         headers: { 'Content-Type': 'application/json' },              } catch (e) {}

              }}

            >        body: JSON.stringify({

              <Bot size={24} />

            </div>          message: userMessage,            }        setError('Server connection failed');// 🔗 PERFECT API CONFIGURATION// 🔗 API CONFIGURATION - MATCHES BACKEND

            <div>

              <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">          conversation_id: currentConversationId

                Advanced AI Assistant

              </h1>        }),          }

              <p className="text-sm text-gray-400">

                Powered by OpenRouter • WizardLM-2-8x22B • {isConnected ? '🟢 Online' : '🔴 Offline'}      });

              </p>

            </div>        }        setConnected(false);

          </div>

        </div>      if (!response.ok) {



        <div className="flex-1 overflow-y-auto">        throw new Error(`Server error: ${response.status}`);      }

          {messages.length === 0 && !streamingContent ? (

            <div className="flex items-center justify-center h-full">      }

              <div className="text-center max-w-md">

                <div     } catch (e) {      }interface Conversation {

                  className="w-20 h-20 rounded-2xl flex items-center justify-center text-white mb-6 mx-auto animate-pulse"

                  style={{       const reader = response.body?.getReader();

                    background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})` 

                  }}      if (!reader) throw new Error('No response stream');      console.error('Error:', e);

                >

                  <Bot size={40} />

                </div>

                <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-4">      let fullResponse = '';    } finally {    } catch (e) {

                  Welcome to Advanced AI

                </h2>      let conversationId = currentConversationId;

                <p className="text-gray-400 text-lg leading-relaxed">

                  Start a conversation with our powerful AI assistant. Ask questions, get help with coding, creative writing, analysis, and much more!      setLoading(false);

                </p>

              </div>      while (true) {

            </div>

          ) : (        const { done, value } = await reader.read();    }      setError('Server not reachable');  id: string;const API_BASE = 'http://localhost:8000/api/v1';const API_BASE = 'http://localhost:8000/api/v1';

            <div className="space-y-6 p-6">

              {messages.map((message) => (        if (done) break;

                <div

                  key={message.id}  };

                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}

                >        const chunk = new TextDecoder().decode(value);

                  <div 

                    className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${        const lines = chunk.split('\n');      setConnected(false);

                      message.role === 'user' 

                        ? 'text-white' 

                        : 'bg-gray-700 text-gray-300'

                    }`}        for (const line of lines) {  return (

                    style={message.role === 'user' ? { 

                      background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`           if (line.startsWith('data: ')) {

                    } : {}}

                  >            const data = line.slice(6);    <div className="flex h-screen bg-gray-50">    }  title: string;

                    {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}

                  </div>            if (data.trim() === '[DONE]') continue;

                  

                  <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>      <div className="flex-1 flex flex-col">

                    <div 

                      className={`inline-block p-4 rounded-2xl backdrop-blur-sm ${            try {

                        message.role === 'user'

                          ? 'text-white'              const parsed = JSON.parse(data);        <div className="border-b bg-white p-4">  };

                          : 'bg-gray-800/50 border border-gray-700/50'

                      }`}              

                      style={message.role === 'user' ? { 

                        background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`               if (parsed.error) {          <h1 className="text-xl font-bold">Perfect ChatGPT Clone</h1>

                      } : {}}

                    >                setError(parsed.error);

                      <p className="whitespace-pre-wrap m-0">{message.content}</p>

                    </div>                continue;          <p className="text-sm text-gray-600">Real AI responses via OpenRouter</p>  created_at: string;

                  </div>

                </div>              }

              ))}

                      </div>

              {streamingContent && (

                <div className="flex gap-4">              if (parsed.conversation_id) {

                  <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-700 flex items-center justify-center">

                    <Bot size={20} className="text-gray-300" />                conversationId = parsed.conversation_id;  const newConv = async () => {

                  </div>

                  <div className="flex-1 max-w-3xl">                if (!currentConversationId) {

                    <div className="inline-block p-4 rounded-2xl bg-gray-800/50 border border-gray-700/50 backdrop-blur-sm">

                      <div className="whitespace-pre-wrap">{streamingContent}</div>                  setCurrentConversationId(conversationId);        <div className="flex-1 overflow-y-auto p-4 space-y-4">

                      <div className="mt-3 flex items-center gap-2 text-blue-400">

                        <div className="flex gap-1">                }

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>              }          {messages.length === 0 ? (    try {  message_count: number;

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>

                        </div>              

                        <span className="text-sm font-medium">AI is thinking...</span>

                      </div>              if (parsed.content) {            <div className="text-center py-20">

                    </div>

                  </div>                fullResponse += parsed.content;

                </div>

              )}                setStreamingContent(fullResponse);              <h2 className="text-2xl font-bold mb-2">Welcome to ChatGPT Clone</h2>      const res = await fetch(`${API_BASE}/conversations`, {



              <div ref={messagesEndRef} />              }

            </div>

          )}                            <p className="text-gray-600">Start chatting with AI!</p>

        </div>

              if (parsed.done) {

        {error && (

          <div className="mx-6 mb-4 bg-red-900/20 border border-red-800/50 text-red-300 px-4 py-3 rounded-xl backdrop-blur-sm">                const assistantMsg: Message = {            </div>        method: 'POST',}interface Message {interface Message {

            <div className="flex items-center gap-2">

              <div className="w-2 h-2 bg-red-500 rounded-full"></div>                  id: (Date.now() + 1).toString(),

              <span className="text-sm font-medium">Error: {error}</span>

            </div>                  role: 'assistant',          ) : (

          </div>

        )}                  content: fullResponse,



        <div className="p-6 bg-gray-800/30 backdrop-blur-xl border-t border-gray-700/50">                  timestamp: new Date().toISOString()            messages.map((msg) => (        headers: { 'Content-Type': 'application/json' },

          <div className="flex gap-4 max-w-4xl mx-auto">

            <div className="flex-1 relative">                };

              <textarea

                ref={textareaRef}                              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>

                value={inputText}

                onChange={(e) => setInputText(e.target.value)}                setMessages(prev => [...prev, assistantMsg]);

                onKeyDown={handleKeyPress}

                placeholder="Message Advanced AI Assistant..."                setStreamingContent('');                <div className={`max-w-lg p-3 rounded-lg ${        body: JSON.stringify({ title: 'New Chat' }),

                disabled={isLoading || !isConnected}

                className="w-full resize-none bg-gray-800/50 border border-gray-700/50 rounded-2xl px-6 py-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent backdrop-blur-sm transition-all duration-200 disabled:opacity-50"                loadConversations();

                style={{ 

                  minHeight: '56px',                break;                  msg.role === 'user' 

                  maxHeight: '200px'

                }}              }

                rows={1}

              />            } catch (parseError) {                    ? 'bg-blue-600 text-white'       });

            </div>

            <button              console.error('Parse error:', parseError);

              onClick={sendMessage}

              disabled={!inputText.trim() || isLoading || !isConnected}            }                    : 'bg-white border'

              className="w-14 h-14 rounded-2xl text-white transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:scale-100 disabled:cursor-not-allowed flex items-center justify-center"

              style={{           }

                background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})` 

              }}        }                }`}>      export default function ChatGPTClone() {  id: string;  id: string;

            >

              {isLoading ? (      }

                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />

              ) : (    } catch (error) {                  {msg.content}

                <Send size={20} />

              )}      console.error('Chat error:', error);

            </button>

          </div>      setError(error instanceof Error ? error.message : 'Failed to send message');                </div>      if (res.ok) {

        </div>

      </div>    } finally {

    </div>

  );      setIsLoading(false);              </div>

}
      setStreamingContent('');

    }            ))        const conv = await res.json();  const [messages, setMessages] = useState<Message[]>([]);

  };

          )}

  // Initialize

  useEffect(() => {          <div ref={endRef} />        setCurrentConvId(conv.id);

    loadConversations();

  }, []);        </div>



  // Handle keyboard events        setMessages([]);  const [inputText, setInputText] = useState('');  role: 'user' | 'assistant';  role: 'user' | 'assistant';

  const handleKeyPress = (e: React.KeyboardEvent) => {

    if (e.key === 'Enter' && !e.shiftKey) {        <div className="border-t bg-white p-4">

      e.preventDefault();

      sendMessage();          <div className="flex gap-2">        setStreaming('');

    }

  };            <input



  // Theme change handler              value={input}        setError('');  const [isLoading, setIsLoading] = useState(false);

  const changeTheme = (themeKey: string) => {

    setCurrentTheme(themeKey);              onChange={(e) => setInput(e.target.value)}

    const theme = themes[themeKey as keyof typeof themes];

    document.documentElement.style.setProperty('--primary-color', theme.primary);              onKeyDown={(e) => e.key === 'Enter' && send()}        loadConvs();

    document.documentElement.style.setProperty('--secondary-color', theme.secondary);

    document.documentElement.style.setProperty('--accent-color', theme.accent);              placeholder="Type your message..."

  };

              className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"      }  const [conversations, setConversations] = useState<Conversation[]>([]);  content: string;  content: string;

  return (

    <div className="flex h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white font-inter">              disabled={loading}

      {/* Sidebar */}

      <div className="w-80 bg-gray-800/50 backdrop-blur-xl border-r border-gray-700/50 flex flex-col">            />    } catch (e) {

        {/* Sidebar Header */}

        <div className="p-6 border-b border-gray-700/50">            <button

          <button

            onClick={createNewConversation}              onClick={send}      setError('Failed to create conversation');  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

            style={{ 

              background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`               disabled={!input.trim() || loading}

            }}

            className="w-full flex items-center gap-3 px-4 py-3 text-white rounded-xl font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg"              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg"    }

          >

            <Plus size={20} />            >

            New Chat

          </button>              {loading ? 'Sending...' : 'Send'}  };  const [streamingContent, setStreamingContent] = useState('');  timestamp: string;  timestamp: string;

          

          {/* Connection Status */}            </button>

          <div className="mt-4 flex items-center gap-2 text-sm text-gray-400">

            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>          </div>

            <span>{isConnected ? 'Connected to AI' : 'Connection Lost'}</span>

          </div>        </div>

        </div>

      </div>  const send = async () => {  const [error, setError] = useState('');

        {/* Chat History */}

        <div className="flex-1 overflow-y-auto p-4 space-y-2">    </div>

          <h3 className="text-sm font-semibold text-gray-400 mb-3">Recent Conversations</h3>

            );    if (!input.trim() || loading) return;

          {conversations.length === 0 ? (

            <div className="text-center py-8 text-gray-500">}

              <Bot size={32} className="mx-auto mb-2 opacity-50" />      const [isConnected, setIsConnected] = useState(false);}}

              <p className="text-sm">No conversations yet</p>

              <p className="text-xs mt-1">Start a new chat to begin</p>    setError('');

            </div>

          ) : (    const msg = input.trim();  

            conversations.map((conv) => (

              <button    setInput('');

                key={conv.id}

                onClick={() => {    setLoading(true);  const messagesEndRef = useRef<HTMLDivElement>(null);

                  setCurrentConversationId(conv.id);

                  setMessages([]);    setStreaming('');

                  setStreamingContent('');

                }}

                className={`w-full text-left p-3 rounded-lg transition-all duration-200 hover:bg-gray-700/50 ${

                  currentConversationId === conv.id     const userMsg = {

                    ? 'bg-gray-700/70 border border-gray-600' 

                    : 'border border-transparent'      id: Date.now().toString(),  const scrollToBottom = () => {interface Conversation {interface Conversation {

                }`}

              >      role: 'user',

                <div className="flex items-start gap-2">

                  <Bot size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />      content: msg,    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

                  <div className="min-w-0 flex-1">

                    <p className="text-sm font-medium text-gray-200 truncate">      timestamp: new Date().toISOString()

                      {conv.title}

                    </p>    };  };  id: string;  id: string;

                    <p className="text-xs text-gray-500 mt-1">

                      {conv.message_count} messages • {new Date(conv.created_at).toLocaleDateString()}    

                    </p>

                  </div>    setMessages(prev => [...prev, userMsg]);

                </div>

              </button>

            ))

          )}    try {  useEffect(() => {  title: string;  created_at: string;

        </div>

      const res = await fetch(`${API_BASE}/chat`, {

        {/* Theme Controls */}

        <div className="p-4 border-t border-gray-700/50">        method: 'POST',    scrollToBottom();

          <div className="flex items-center gap-2 mb-3">

            <Palette size={16} className="text-gray-400" />        headers: { 'Content-Type': 'application/json' },

            <span className="text-sm font-medium text-gray-300">Themes</span>

          </div>        body: JSON.stringify({  }, [messages, streamingContent]);  created_at: string;  message_count: number;

          <div className="grid grid-cols-3 gap-2">

            {Object.entries(themes).map(([key, theme]) => (          message: msg,

              <button

                key={key}          conversation_id: currentConvId

                onClick={() => changeTheme(key)}

                className={`w-10 h-10 rounded-lg transition-all duration-200 hover:scale-110 ${        }),

                  currentTheme === key ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-800' : ''

                }`}      });  const loadConversations = async () => {  message_count: number;}

                style={{ background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})` }}

                title={theme.name}

              />

            ))}      if (!res.ok) throw new Error(`Server error: ${res.status}`);    try {

          </div>

        </div>

      </div>

      const reader = res.body?.getReader();      const response = await fetch(`${API_BASE}/conversations`);}

      {/* Main Chat Area */}

      <div className="flex-1 flex flex-col">      if (!reader) throw new Error('No response stream');

        {/* Chat Header */}

        <div className="p-6 bg-gray-800/30 backdrop-blur-xl border-b border-gray-700/50">      if (response.ok) {

          <div className="flex items-center gap-3">

            <div       let fullRes = '';

              className="w-12 h-12 rounded-xl flex items-center justify-center text-white"

              style={{       let convId = currentConvId;        const data = await response.json();export default function ChatGPTClone() {

                background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})` 

              }}

            >

              <Bot size={24} />      while (true) {        setConversations(data.conversations || []);

            </div>

            <div>        const { done, value } = await reader.read();

              <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">

                Advanced AI Assistant        if (done) break;        setIsConnected(true);export default function PerfectChatGPTClone() {  // 📝 STATE MANAGEMENT

              </h1>

              <p className="text-sm text-gray-400">

                Powered by OpenRouter • WizardLM-2-8x22B • {isConnected ? '🟢 Online' : '🔴 Offline'}

              </p>        const chunk = new TextDecoder().decode(value);        setError('');

            </div>

          </div>        const lines = chunk.split('\n');

        </div>

      } else {  // 📝 PERFECT STATE MANAGEMENT  const [messages, setMessages] = useState<Message[]>([]);

        {/* Messages Area */}

        <div className="flex-1 overflow-y-auto">        for (const line of lines) {

          {messages.length === 0 && !streamingContent ? (

            <div className="flex items-center justify-center h-full">          if (line.startsWith('data: ')) {        setError('Failed to connect to server');

              <div className="text-center max-w-md">

                <div             const data = line.slice(6);

                  className="w-20 h-20 rounded-2xl flex items-center justify-center text-white mb-6 mx-auto animate-pulse"

                  style={{             if (data.trim() === '[DONE]') continue;        setIsConnected(false);  const [messages, setMessages] = useState<Message[]>([]);  const [inputText, setInputText] = useState('');

                    background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})` 

                  }}

                >

                  <Bot size={40} />            try {      }

                </div>

                <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-4">              const parsed = JSON.parse(data);

                  Welcome to Advanced AI

                </h2>                  } catch (error) {  const [inputText, setInputText] = useState('');  const [isLoading, setIsLoading] = useState(false);

                <p className="text-gray-400 text-lg leading-relaxed">

                  Start a conversation with our powerful AI assistant. Ask questions, get help with coding, creative writing, analysis, and much more!              if (parsed.error) {

                </p>

              </div>                setError(parsed.error);      console.error('Connection error:', error);

            </div>

          ) : (                continue;

            <div className="space-y-6 p-6">

              {messages.map((message) => (              }      setError('Server not reachable');  const [isLoading, setIsLoading] = useState(false);  const [conversations, setConversations] = useState<Conversation[]>([]);

                <div

                  key={message.id}              

                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}

                >              if (parsed.conversation_id) {      setIsConnected(false);

                  {/* Avatar */}

                  <div                 convId = parsed.conversation_id;

                    className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${

                      message.role === 'user'                 if (!currentConvId) setCurrentConvId(convId);    }  const [conversations, setConversations] = useState<Conversation[]>([]);  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

                        ? 'text-white' 

                        : 'bg-gray-700 text-gray-300'              }

                    }`}

                    style={message.role === 'user' ? {                 };

                      background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})` 

                    } : {}}              if (parsed.content) {

                  >

                    {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}                fullRes += parsed.content;  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);  const [streamingContent, setStreamingContent] = useState('');

                  </div>

                                  setStreaming(fullRes);

                  {/* Message Content */}

                  <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>              }  const createNewConversation = async () => {

                    <div 

                      className={`inline-block p-4 rounded-2xl backdrop-blur-sm ${              

                        message.role === 'user'

                          ? 'text-white'              if (parsed.done) {    try {  const [streamingContent, setStreamingContent] = useState('');  const [error, setError] = useState('');

                          : 'bg-gray-800/50 border border-gray-700/50'

                      }`}                const aiMsg = {

                      style={message.role === 'user' ? { 

                        background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`                   id: (Date.now() + 1).toString(),      const response = await fetch(`${API_BASE}/conversations`, {

                      } : {}}

                    >                  role: 'assistant',

                      <div className="prose prose-invert max-w-none">

                        <p className="whitespace-pre-wrap m-0">{message.content}</p>                  content: fullRes,        method: 'POST',  const [error, setError] = useState('');  

                      </div>

                    </div>                  timestamp: new Date().toISOString()

                  </div>

                </div>                };        headers: { 'Content-Type': 'application/json' },

              ))}

                

              {/* Streaming Message */}

              {streamingContent && (                setMessages(prev => [...prev, aiMsg]);        body: JSON.stringify({ title: 'New Chat' }),  const [isConnected, setIsConnected] = useState(false);  const messagesEndRef = useRef<HTMLDivElement>(null);

                <div className="flex gap-4">

                  <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-700 flex items-center justify-center">                setStreaming('');

                    <Bot size={20} className="text-gray-300" />

                  </div>                loadConvs();      });

                  <div className="flex-1 max-w-3xl">

                    <div className="inline-block p-4 rounded-2xl bg-gray-800/50 border border-gray-700/50 backdrop-blur-sm">                break;

                      <div className="prose prose-invert max-w-none">

                        <div className="whitespace-pre-wrap">{streamingContent}</div>              }        

                      </div>

                      <div className="mt-3 flex items-center gap-2 text-blue-400">            } catch (e) {

                        <div className="flex gap-1">

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>              console.error('Parse error:', e);      if (response.ok) {

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>

                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>            }

                        </div>

                        <span className="text-sm font-medium">AI is thinking...</span>          }        const newConversation = await response.json();  const messagesEndRef = useRef<HTMLDivElement>(null);  // 🎯 AUTO SCROLL TO BOTTOM

                      </div>

                    </div>        }

                  </div>

                </div>      }        setCurrentConversationId(newConversation.id);

              )}

    } catch (e) {

              <div ref={messagesEndRef} />

            </div>      setError(e.message || 'Failed to send message');        setMessages([]);  const textareaRef = useRef<HTMLTextAreaElement>(null);  const scrollToBottom = () => {

          )}

        </div>    } finally {



        {/* Error Display */}      setLoading(false);        setStreamingContent('');

        {error && (

          <div className="mx-6 mb-4 bg-red-900/20 border border-red-800/50 text-red-300 px-4 py-3 rounded-xl backdrop-blur-sm">      setStreaming('');

            <div className="flex items-center gap-2">

              <div className="w-2 h-2 bg-red-500 rounded-full"></div>    }        setError('');    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

              <span className="text-sm font-medium">Error: {error}</span>

            </div>  };

          </div>

        )}        loadConversations();



        {/* Input Area */}  useEffect(() => { loadConvs(); }, []);

        <div className="p-6 bg-gray-800/30 backdrop-blur-xl border-t border-gray-700/50">

          <div className="flex gap-4 max-w-4xl mx-auto">      }  // 🎯 PERFECT AUTO SCROLL  };

            <div className="flex-1 relative">

              <textarea  const handleKey = (e) => {

                ref={textareaRef}

                value={inputText}    if (e.key === 'Enter' && !e.shiftKey) {    } catch (error) {

                onChange={(e) => setInputText(e.target.value)}

                onKeyDown={handleKeyPress}      e.preventDefault();

                placeholder="Message Advanced AI Assistant..."

                disabled={isLoading || !isConnected}      send();      console.error('Failed to create conversation:', error);  const scrollToBottom = () => {

                className="w-full resize-none bg-gray-800/50 border border-gray-700/50 rounded-2xl px-6 py-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent backdrop-blur-sm transition-all duration-200 disabled:opacity-50"

                style={{     }

                  minHeight: '56px',

                  maxHeight: '200px'  };      setError('Failed to create new conversation');

                }}

                rows={1}

              />

            </div>  return (    }    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });  useEffect(() => {

            <button

              onClick={sendMessage}    <div className="flex h-screen bg-gray-50">

              disabled={!inputText.trim() || isLoading || !isConnected}

              className="w-14 h-14 rounded-2xl text-white transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:scale-100 disabled:cursor-not-allowed flex items-center justify-center"      {/* Sidebar */}  };

              style={{ 

                background: `linear-gradient(135deg, ${themes[currentTheme as keyof typeof themes].primary}, ${themes[currentTheme as keyof typeof themes].secondary})`       <div className="w-80 bg-white border-r flex flex-col">

              }}

            >        <div className="p-4 border-b">  };    scrollToBottom();

              {isLoading ? (

                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />          <button

              ) : (

                <Send size={20} />            onClick={newConv}  const loadConversation = async (conversationId: string) => {

              )}

            </button>            className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"

          </div>

        </div>          >    try {  }, [messages, streamingContent]);

      </div>

    </div>            <Plus size={20} />

  );

}            New Chat      const response = await fetch(`${API_BASE}/conversations/${conversationId}`);

          </button>

                if (response.ok) {  useEffect(() => {

          <div className="mt-3 flex items-center gap-2 text-sm">

            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>        const data = await response.json();

            <span className="text-gray-600">

              {connected ? 'Connected' : 'Disconnected'}        setMessages(data.messages || []);    scrollToBottom();  // 🔄 LOAD CONVERSATIONS

            </span>

          </div>        setCurrentConversationId(conversationId);

        </div>

        setStreamingContent('');  }, [messages, streamingContent]);  const loadConversations = async () => {

        <div className="flex-1 overflow-y-auto p-3">

          <h3 className="text-sm font-semibold text-gray-600 mb-3">Conversations</h3>        setError('');

          

          {conversations.length === 0 ? (      }    try {

            <div className="text-center py-8 text-gray-500">

              <p className="text-sm">No conversations yet</p>    } catch (error) {

            </div>

          ) : (      console.error('Failed to load conversation:', error);  // 🔄 PERFECT LOAD CONVERSATIONS      const response = await fetch(`${API_BASE}/conversations`);

            conversations.map((conv) => (

              <button      setError('Failed to load conversation');

                key={conv.id}

                onClick={() => {    }  const loadConversations = async () => {      if (response.ok) {

                  setCurrentConvId(conv.id);

                  setMessages([]);  };

                  setStreaming('');

                }}    try {        const data = await response.json();

                className={`w-full text-left p-3 rounded-lg mb-2 transition-all hover:bg-gray-50 ${

                  currentConvId === conv.id ? 'bg-blue-50 border border-blue-200' : ''  const sendMessage = async () => {

                }`}

              >    if (!inputText.trim() || isLoading) return;      const response = await fetch(`${API_BASE}/conversations`);        setConversations(data.conversations || []);

                <p className="text-sm font-medium text-gray-900 truncate">

                  {conv.title}    

                </p>

                <p className="text-xs text-gray-500 mt-1">    setError('');      if (response.ok) {      }

                  {conv.message_count} messages

                </p>    const userMessage = inputText.trim();

              </button>

            ))    setInputText('');        const data = await response.json();    } catch (error) {

          )}

        </div>    setIsLoading(true);

      </div>

    setStreamingContent('');        setConversations(data.conversations || []);      console.error('Failed to load conversations:', error);

      {/* Chat Area */}

      <div className="flex-1 flex flex-col">

        <div className="border-b bg-white px-6 py-4">

          <div className="flex items-center gap-3">    const userMsg: Message = {        setIsConnected(true);    }

            <div className="p-2 bg-blue-100 rounded-lg">

              <Bot size={20} className="text-blue-600" />      id: Date.now().toString(),

            </div>

            <div>      role: 'user',        setError('');  };

              <h1 className="text-lg font-semibold text-gray-900">

                Perfect ChatGPT Clone      content: userMessage,

              </h1>

              <p className="text-sm text-gray-600">      timestamp: new Date().toISOString()      } else {

                WizardLM-2-8x22B • {connected ? '🟢 Online' : '🔴 Offline'}

              </p>    };

            </div>

          </div>            setError('Failed to connect to server');  // 🆕 CREATE NEW CONVERSATION

        </div>

    setMessages(prev => [...prev, userMsg]);

        <div className="flex-1 overflow-y-auto">

          {messages.length === 0 && !streaming ? (        setIsConnected(false);  const createNewConversation = async () => {

            <div className="flex items-center justify-center h-full">

              <div className="text-center">    try {

                <div className="p-4 bg-blue-100 rounded-full inline-block mb-4">

                  <Bot size={32} className="text-blue-600" />      const response = await fetch(`${API_BASE}/chat`, {      }    try {

                </div>

                <h2 className="text-xl font-semibold text-gray-900 mb-2">        method: 'POST',

                  Welcome to Perfect ChatGPT Clone

                </h2>        headers: { 'Content-Type': 'application/json' },    } catch (error) {      const response = await fetch(`${API_BASE}/conversations`, {

                <p className="text-gray-600">Start a conversation with AI!</p>

              </div>        body: JSON.stringify({

            </div>

          ) : (          message: userMessage,      console.error('Connection error:', error);        method: 'POST',

            <div className="space-y-6 p-6">

              {messages.map((msg) => (          conversation_id: currentConversationId

                <div

                  key={msg.id}        }),      setError('Server not reachable');        headers: { 'Content-Type': 'application/json' },

                  className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}

                >      });

                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${

                    msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'      setIsConnected(false);        body: JSON.stringify({ title: 'New Chat' }),

                  }`}>

                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}      if (!response.ok) {

                  </div>

                          throw new Error(`Server error: ${response.status}`);    }      });

                  <div className={`flex-1 max-w-3xl ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>

                    <div className={`inline-block p-4 rounded-xl ${      }

                      msg.role === 'user'

                        ? 'bg-blue-600 text-white'  };      

                        : 'bg-white border'

                    }`}>      const reader = response.body?.getReader();

                      <p className="whitespace-pre-wrap">{msg.content}</p>

                    </div>      if (!reader) throw new Error('No response stream');      if (response.ok) {

                  </div>

                </div>

              ))}

      let fullResponse = '';  // 🆕 PERFECT NEW CONVERSATION        const newConversation = await response.json();

              {streaming && (

                <div className="flex gap-4">      let conversationId = currentConversationId;

                  <div className="w-8 h-8 rounded-lg bg-gray-200 flex items-center justify-center">

                    <Bot size={16} className="text-gray-600" />  const createNewConversation = async () => {        setCurrentConversationId(newConversation.id);

                  </div>

                  <div className="flex-1 max-w-3xl">      while (true) {

                    <div className="inline-block p-4 rounded-xl bg-white border">

                      <p className="whitespace-pre-wrap">{streaming}</p>        const { done, value } = await reader.read();    try {        setMessages([]);

                      <div className="mt-2 flex items-center gap-2 text-blue-500">

                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>        if (done) break;

                        <span className="text-sm">AI is typing...</span>

                      </div>      const response = await fetch(`${API_BASE}/conversations`, {        setStreamingContent('');

                    </div>

                  </div>        const chunk = new TextDecoder().decode(value);

                </div>

              )}        const lines = chunk.split('\n');        method: 'POST',        loadConversations();



              <div ref={endRef} />

            </div>

          )}        for (const line of lines) {        headers: { 'Content-Type': 'application/json' },      }

        </div>

          if (line.startsWith('data: ')) {

        {error && (

          <div className="mx-6 mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">            const data = line.slice(6);        body: JSON.stringify({ title: 'New Chat' }),    } catch (error) {

            <span className="text-sm">Error: {error}</span>

          </div>            if (data.trim() === '[DONE]') continue;

        )}

      });      console.error('Failed to create conversation:', error);

        <div className="border-t bg-white p-6">

          <div className="flex gap-4">            try {

            <textarea

              value={input}              const parsed = JSON.parse(data);          }

              onChange={(e) => setInput(e.target.value)}

              onKeyDown={handleKey}              

              placeholder="Type your message... (Enter to send)"

              disabled={loading || !connected}              if (parsed.error) {      if (response.ok) {  };

              className="flex-1 resize-none border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"

              rows={1}                setError(parsed.error);

              style={{ minHeight: '50px', maxHeight: '120px' }}

            />                continue;        const newConversation = await response.json();

            <button

              onClick={send}              }

              disabled={!input.trim() || loading || !connected}

              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-6 py-3 rounded-xl transition-colors flex items-center gap-2"                      setCurrentConversationId(newConversation.id);  // 📖 LOAD CONVERSATION MESSAGES

            >

              {loading ? (              if (parsed.conversation_id) {

                <>

                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />                conversationId = parsed.conversation_id;        setMessages([]);  const loadConversation = async (conversationId: string) => {

                  <span>Sending</span>

                </>                if (!currentConversationId) {

              ) : (

                <>                  setCurrentConversationId(conversationId);        setStreamingContent('');    try {

                  <Send size={16} />

                  <span>Send</span>                }

                </>

              )}              }        setError('');      const response = await fetch(`${API_BASE}/conversations/${conversationId}`);

            </button>

          </div>              

        </div>

      </div>              if (parsed.content) {        loadConversations();      if (response.ok) {

    </div>

  );                fullResponse += parsed.content;

}
                setStreamingContent(fullResponse);      }        const data = await response.json();

              }

                  } catch (error) {        setMessages(data.messages || []);

              if (parsed.done) {

                const assistantMsg: Message = {      console.error('Failed to create conversation:', error);        setCurrentConversationId(conversationId);

                  id: (Date.now() + 1).toString(),

                  role: 'assistant',      setError('Failed to create new conversation');        setStreamingContent('');

                  content: fullResponse,

                  timestamp: new Date().toISOString()    }      }

                };

                  };    } catch (error) {

                setMessages(prev => [...prev, assistantMsg]);

                setStreamingContent('');      console.error('Failed to load conversation:', error);

                loadConversations();

                break;  // 📖 PERFECT LOAD CONVERSATION    }

              }

            } catch (parseError) {  const loadConversation = async (conversationId: string) => {  };

              console.error('Parse error:', parseError);

            }    try {

          }

        }      const response = await fetch(`${API_BASE}/conversations/${conversationId}`);  // 💬 SEND MESSAGE WITH STREAMING

      }

    } catch (error) {      if (response.ok) {  const sendMessage = async () => {

      console.error('Chat error:', error);

      setError(error instanceof Error ? error.message : 'Failed to send message');        const data = await response.json();    if (!inputText.trim() || isLoading) return;

    } finally {

      setIsLoading(false);        setMessages(data.messages || []);    

      setStreamingContent('');

    }        setCurrentConversationId(conversationId);    setError('');

  };

        setStreamingContent('');    const userMessage = inputText.trim();

  const MarkdownComponents = {

    code({ node, inline, className, children, ...props }: any) {        setError('');    setInputText('');

      const match = /language-(\w+)/.exec(className || '');

      return !inline && match ? (      }    setIsLoading(true);

        <SyntaxHighlighter

          style={oneDark}    } catch (error) {    setStreamingContent('');

          language={match[1]}

          PreTag="div"      console.error('Failed to load conversation:', error);

          className="rounded-lg my-3 text-sm"

          {...props}      setError('Failed to load conversation');    // Add user message immediately

        >

          {String(children).replace(/\n$/, '')}    }    const userMsg: Message = {

        </SyntaxHighlighter>

      ) : (  };      id: Date.now().toString(),

        <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono" {...props}>

          {children}      role: 'user',

        </code>

      );  // 💬 PERFECT SEND MESSAGE      content: userMessage,

    },

  };  const sendMessage = async () => {      timestamp: new Date().toISOString()



  useEffect(() => {    if (!inputText.trim() || isLoading) return;    };

    loadConversations();

  }, []);        



  const handleKeyPress = (e: React.KeyboardEvent) => {    setError('');    setMessages(prev => [...prev, userMsg]);

    if (e.key === 'Enter' && !e.shiftKey) {

      e.preventDefault();    const userMessage = inputText.trim();

      sendMessage();

    }    setInputText('');    try {

  };

    setIsLoading(true);      const response = await fetch(`${API_BASE}/chat`, {

  return (

    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">    setStreamingContent('');        method: 'POST',

      {/* Sidebar */}

      <div className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">        headers: { 'Content-Type': 'application/json' },

        <div className="p-4 border-b border-gray-200 dark:border-gray-800">

          <button    // Add user message immediately        body: JSON.stringify({

            onClick={createNewConversation}

            className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"    const userMsg: Message = {          message: userMessage,

          >

            <Plus size={20} />      id: Date.now().toString(),          conversation_id: currentConversationId

            New Chat

          </button>      role: 'user',        }),

          

          <div className="mt-3 flex items-center gap-2 text-sm">      content: userMessage,      });

            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>

            <span className="text-gray-600 dark:text-gray-400">      timestamp: new Date().toISOString()

              {isConnected ? 'Connected' : 'Disconnected'}

            </span>    };      if (!response.ok) {

          </div>

        </div>            throw new Error(`Server error: ${response.status}`);



        <div className="flex-1 overflow-y-auto p-3">    setMessages(prev => [...prev, userMsg]);      }

          <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-3">

            Recent Conversations

          </h3>

              try {      const reader = response.body?.getReader();

          {conversations.length === 0 ? (

            <div className="text-center py-8 text-gray-500 dark:text-gray-400">      const response = await fetch(`${API_BASE}/chat`, {      if (!reader) throw new Error('No response stream');

              <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />

              <p className="text-sm">No conversations yet</p>        method: 'POST',

              <p className="text-xs mt-1">Start a new chat to begin</p>

            </div>        headers: { 'Content-Type': 'application/json' },      let fullResponse = '';

          ) : (

            conversations.map((conv) => (        body: JSON.stringify({      let conversationId = currentConversationId;

              <button

                key={conv.id}          message: userMessage,

                onClick={() => loadConversation(conv.id)}

                className={`w-full text-left p-3 rounded-lg mb-2 transition-all hover:bg-gray-50 dark:hover:bg-gray-800 ${          conversation_id: currentConversationId      while (true) {

                  currentConversationId === conv.id

                    ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'        }),        const { done, value } = await reader.read();

                    : 'border border-transparent'

                }`}      });        if (done) break;

              >

                <div className="flex items-start gap-2">

                  <MessageSquare size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />

                  <div className="min-w-0 flex-1">      if (!response.ok) {        const chunk = new TextDecoder().decode(value);

                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">

                      {conv.title}        throw new Error(`Server error: ${response.status}`);        const lines = chunk.split('\n');

                    </p>

                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">      }

                      {conv.message_count} messages • {new Date(conv.created_at).toLocaleDateString()}

                    </p>        for (const line of lines) {

                  </div>

                </div>      const reader = response.body?.getReader();          if (line.startsWith('data: ')) {

              </button>

            ))      if (!reader) throw new Error('No response stream');            const data = line.slice(6);

          )}

        </div>            if (data.trim() === '[DONE]') continue;

      </div>

      let fullResponse = '';

      {/* Chat Area */}

      <div className="flex-1 flex flex-col">      let conversationId = currentConversationId;            try {

        <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4">

          <div className="flex items-center gap-3">              const parsed = JSON.parse(data);

            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">

              <Bot size={20} className="text-blue-600 dark:text-blue-400" />      while (true) {              

            </div>

            <div>        const { done, value } = await reader.read();              if (parsed.error) {

              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">

                Perfect ChatGPT Clone        if (done) break;                setError(parsed.error);

              </h1>

              <p className="text-sm text-gray-600 dark:text-gray-400">                continue;

                Powered by WizardLM-2-8x22B • {isConnected ? '🟢 Online' : '🔴 Offline'}

              </p>        const chunk = new TextDecoder().decode(value);              }

            </div>

          </div>        const lines = chunk.split('\n');              

        </div>

              if (parsed.conversation_id) {

        <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-950">

          {messages.length === 0 && !streamingContent ? (        for (const line of lines) {                conversationId = parsed.conversation_id;

            <div className="flex items-center justify-center h-full">

              <div className="text-center max-w-md">          if (line.startsWith('data: ')) {                if (!currentConversationId) {

                <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded-full inline-block mb-4">

                  <Bot size={32} className="text-blue-600 dark:text-blue-400" />            const data = line.slice(6);                  setCurrentConversationId(conversationId);

                </div>

                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">            if (data.trim() === '[DONE]') continue;                }

                  Welcome to Perfect ChatGPT Clone

                </h2>              }

                <p className="text-gray-600 dark:text-gray-400 mb-4">

                  Start a conversation with AI. Ask anything!            try {              

                </p>

              </div>              const parsed = JSON.parse(data);              if (parsed.content) {

            </div>

          ) : (                              fullResponse += parsed.content;

            <div className="space-y-6 p-6">

              {messages.map((message) => (              if (parsed.error) {                setStreamingContent(fullResponse);

                <div

                  key={message.id}                setError(parsed.error);              }

                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}

                >                continue;              

                  <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${

                    message.role === 'user'               }              if (parsed.done) {

                      ? 'bg-blue-600 text-white' 

                      : 'bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400'                              // Add complete assistant message

                  }`}>

                    {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}              if (parsed.conversation_id) {                const assistantMsg: Message = {

                  </div>

                                  conversationId = parsed.conversation_id;                  id: (Date.now() + 1).toString(),

                  <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>

                    <div className={`inline-block p-4 rounded-xl ${                if (!currentConversationId) {                  role: 'assistant',

                      message.role === 'user'

                        ? 'bg-blue-600 text-white'                  setCurrentConversationId(conversationId);                  content: fullResponse,

                        : 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-800'

                    }`}>                }                  timestamp: new Date().toISOString()

                      {message.role === 'user' ? (

                        <p className="whitespace-pre-wrap">{message.content}</p>              }                };

                      ) : (

                        <div className="prose prose-sm dark:prose-invert max-w-none">                              

                          <ReactMarkdown components={MarkdownComponents}>

                            {message.content}              if (parsed.content) {                setMessages(prev => [...prev, assistantMsg]);

                          </ReactMarkdown>

                        </div>                fullResponse += parsed.content;                setStreamingContent('');

                      )}

                    </div>                setStreamingContent(fullResponse);                loadConversations(); // Refresh conversation list

                  </div>

                </div>              }                break;

              ))}

                            }

              {streamingContent && (

                <div className="flex gap-4">              if (parsed.done) {            } catch (parseError) {

                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-800 flex items-center justify-center">

                    <Bot size={16} className="text-gray-600 dark:text-gray-400" />                // Add complete assistant message              console.error('Parse error:', parseError);

                  </div>

                  <div className="flex-1 max-w-3xl">                const assistantMsg: Message = {            }

                    <div className="inline-block p-4 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800">

                      <div className="prose prose-sm dark:prose-invert max-w-none">                  id: (Date.now() + 1).toString(),          }

                        <ReactMarkdown components={MarkdownComponents}>

                          {streamingContent}                  role: 'assistant',        }

                        </ReactMarkdown>

                      </div>                  content: fullResponse,      }

                      <div className="mt-3 flex items-center gap-2 text-blue-500">

                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>                  timestamp: new Date().toISOString()    } catch (error) {

                        <span className="text-sm font-medium">AI is typing...</span>

                      </div>                };      console.error('Chat error:', error);

                    </div>

                  </div>                      setError(error instanceof Error ? error.message : 'Failed to send message');

                </div>

              )}                setMessages(prev => [...prev, assistantMsg]);    } finally {



              <div ref={messagesEndRef} />                setStreamingContent('');      setIsLoading(false);

            </div>

          )}                loadConversations(); // Refresh conversation list      setStreamingContent('');

        </div>

                break;    }

        {error && (

          <div className="mx-6 mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg">              }  };

            <div className="flex items-center gap-2">

              <div className="w-2 h-2 bg-red-500 rounded-full"></div>            } catch (parseError) {

              <span className="text-sm font-medium">Error: {error}</span>

            </div>              console.error('Parse error:', parseError);  // 🎨 MARKDOWN COMPONENTS

          </div>

        )}            }  const MarkdownComponents = {



        <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6">          }    code({ node, inline, className, children, ...props }: any) {

          <div className="flex gap-4">

            <div className="flex-1 relative">        }      const match = /language-(\w+)/.exec(className || '');

              <textarea

                value={inputText}      }      return !inline && match ? (

                onChange={(e) => setInputText(e.target.value)}

                onKeyDown={handleKeyPress}    } catch (error) {        <SyntaxHighlighter

                placeholder="Type your message... (Enter to send, Shift+Enter for new line)"

                disabled={isLoading || !isConnected}      console.error('Chat error:', error);          style={oneDark}

                className="w-full resize-none border border-gray-300 dark:border-gray-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50 transition-colors"

                rows={1}      setError(error instanceof Error ? error.message : 'Failed to send message');          language={match[1]}

                style={{ minHeight: '50px', maxHeight: '120px' }}

              />    } finally {          PreTag="div"

            </div>

            <button      setIsLoading(false);          className="rounded-md my-2"

              onClick={sendMessage}

              disabled={!inputText.trim() || isLoading || !isConnected}      setStreamingContent('');          {...props}

              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl transition-colors font-medium flex items-center gap-2"

            >    }        >

              {isLoading ? (

                <>  };          {String(children).replace(/\n$/, '')}

                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />

                  <span>Sending...</span>        </SyntaxHighlighter>

                </>

              ) : (  // 🎨 PERFECT MARKDOWN COMPONENTS      ) : (

                <>

                  <Send size={16} />  const PerfectMarkdownComponents = {        <code className="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm" {...props}>

                  <span>Send</span>

                </>    code({ node, inline, className, children, ...props }: any) {          {children}

              )}

            </button>      const match = /language-(\w+)/.exec(className || '');        </code>

          </div>

        </div>      return !inline && match ? (      );

      </div>

    </div>        <SyntaxHighlighter    },

  );

}          style={oneDark}  };

          language={match[1]}

          PreTag="div"  // 🔄 LOAD CONVERSATIONS ON MOUNT

          className="rounded-lg my-3 text-sm"  useEffect(() => {

          {...props}    loadConversations();

        >  }, []);

          {String(children).replace(/\n$/, '')}

        </SyntaxHighlighter>  // ⌨️ HANDLE ENTER KEY

      ) : (  const handleKeyPress = (e: React.KeyboardEvent) => {

        <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono" {...props}>    if (e.key === 'Enter' && !e.shiftKey) {

          {children}      e.preventDefault();

        </code>      sendMessage();

      );    }

    },  };

    h1: ({ children }: any) => <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">{children}</h1>,

    h2: ({ children }: any) => <h2 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">{children}</h2>,  return (

    h3: ({ children }: any) => <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">{children}</h3>,    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">

    p: ({ children }: any) => <p className="mb-3 text-gray-800 dark:text-gray-200 leading-relaxed">{children}</p>,      {/* 📱 SIDEBAR */}

    ul: ({ children }: any) => <ul className="mb-3 ml-4 list-disc text-gray-800 dark:text-gray-200">{children}</ul>,      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">

    ol: ({ children }: any) => <ol className="mb-3 ml-4 list-decimal text-gray-800 dark:text-gray-200">{children}</ol>,        {/* New Chat Button */}

    li: ({ children }: any) => <li className="mb-1">{children}</li>,        <div className="p-4 border-b border-gray-200 dark:border-gray-700">

    blockquote: ({ children }: any) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic mb-3 text-gray-700 dark:text-gray-300">{children}</blockquote>,          <button

  };            onClick={createNewConversation}

            className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"

  // 🔄 PERFECT INITIALIZATION          >

  useEffect(() => {            <Plus size={20} />

    loadConversations();            New Chat

  }, []);          </button>

        </div>

  // ⌨️ PERFECT KEYBOARD HANDLING

  const handleKeyPress = (e: React.KeyboardEvent) => {        {/* Conversations List */}

    if (e.key === 'Enter' && !e.shiftKey) {        <div className="flex-1 overflow-y-auto p-2">

      e.preventDefault();          <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-3 px-2">

      sendMessage();            Recent Conversations

    }          </h3>

  };          {conversations.map((conv) => (

            <button

  // 🎨 PERFECT TEXTAREA AUTO-RESIZE              key={conv.id}

  useEffect(() => {              onClick={() => loadConversation(conv.id)}

    const textarea = textareaRef.current;              className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${

    if (textarea) {                currentConversationId === conv.id

      textarea.style.height = 'auto';                  ? 'bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-600'

      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'

    }              }`}

  }, [inputText]);            >

              <div className="flex items-center gap-2">

  return (                <MessageSquare size={16} className="text-gray-500" />

    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">                <span className="text-sm text-gray-700 dark:text-gray-300 truncate">

      {/* 📱 PERFECT SIDEBAR */}                  Chat ({conv.message_count} messages)

      <div className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col shadow-sm">                </span>

        {/* Perfect Header */}              </div>

        <div className="p-4 border-b border-gray-200 dark:border-gray-800">              <div className="text-xs text-gray-500 mt-1">

          <button                {new Date(conv.created_at).toLocaleDateString()}

            onClick={createNewConversation}              </div>

            className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"            </button>

          >          ))}

            <Plus size={20} />        </div>

            New Chat      </div>

          </button>

                {/* 💬 CHAT AREA */}

          {/* Connection Status */}      <div className="flex-1 flex flex-col">

          <div className="mt-3 flex items-center gap-2 text-sm">        {/* Header */}

            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>        <div className="border-b border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">

            <span className="text-gray-600 dark:text-gray-400">          <h1 className="text-xl font-semibold text-gray-800 dark:text-white">

              {isConnected ? 'Connected' : 'Disconnected'}            ChatGPT Clone

            </span>          </h1>

          </div>          <p className="text-sm text-gray-600 dark:text-gray-400">

        </div>            Powered by WizardLM-2-8x22B via OpenRouter

          </p>

        {/* Perfect Conversations List */}        </div>

        <div className="flex-1 overflow-y-auto">

          <div className="p-3">        {/* Messages */}

            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-3">        <div className="flex-1 overflow-y-auto p-4 space-y-6">

              Recent Conversations          {messages.map((message) => (

            </h3>            <div

                          key={message.id}

            {conversations.length === 0 ? (              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}

              <div className="text-center py-8 text-gray-500 dark:text-gray-400">            >

                <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />              <div

                <p className="text-sm">No conversations yet</p>                className={`max-w-3xl px-4 py-3 rounded-2xl ${

                <p className="text-xs mt-1">Start a new chat to begin</p>                  message.role === 'user'

              </div>                    ? 'bg-blue-600 text-white'

            ) : (                    : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700'

              conversations.map((conv) => (                }`}

                <button              >

                  key={conv.id}                {message.role === 'user' ? (

                  onClick={() => loadConversation(conv.id)}                  <p className="whitespace-pre-wrap">{message.content}</p>

                  className={`w-full text-left p-3 rounded-lg mb-2 transition-all hover:bg-gray-50 dark:hover:bg-gray-800 ${                ) : (

                    currentConversationId === conv.id                  <div className="prose dark:prose-invert max-w-none">

                      ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'                    <ReactMarkdown components={MarkdownComponents}>

                      : 'border border-transparent'                      {message.content}

                  }`}                    </ReactMarkdown>

                >                  </div>

                  <div className="flex items-start gap-2">                )}

                    <MessageSquare size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />              </div>

                    <div className="min-w-0 flex-1">            </div>

                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">          ))}

                        {conv.title}

                      </p>          {/* Streaming Message */}

                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">          {streamingContent && (

                        {conv.message_count} messages • {new Date(conv.created_at).toLocaleDateString()}            <div className="flex justify-start">

                      </p>              <div className="max-w-3xl px-4 py-3 rounded-2xl bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700">

                    </div>                <div className="prose dark:prose-invert max-w-none">

                  </div>                  <ReactMarkdown components={MarkdownComponents}>

                </button>                    {streamingContent}

              ))                  </ReactMarkdown>

            )}                </div>

          </div>                <div className="mt-2 text-blue-500">

        </div>                  <span className="animate-pulse">●</span> Typing...

      </div>                </div>

              </div>

      {/* 💬 PERFECT CHAT AREA */}            </div>

      <div className="flex-1 flex flex-col">          )}

        {/* Perfect Header */}

        <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4 shadow-sm">          {/* Error Display */}

          <div className="flex items-center gap-3">          {error && (

            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded">

              <Bot size={20} className="text-blue-600 dark:text-blue-400" />              ❌ Error: {error}

            </div>            </div>

            <div>          )}

              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">

                Perfect ChatGPT Clone          <div ref={messagesEndRef} />

              </h1>        </div>

              <p className="text-sm text-gray-600 dark:text-gray-400">

                Powered by WizardLM-2-8x22B • {isConnected ? '🟢 Online' : '🔴 Offline'}        {/* Input Area */}

              </p>        <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">

            </div>          <div className="flex gap-3">

          </div>            <textarea

        </div>              value={inputText}

              onChange={(e) => setInputText(e.target.value)}

        {/* Perfect Messages Area */}              onKeyDown={handleKeyPress}

        <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-950">              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"

          {messages.length === 0 && !streamingContent ? (              disabled={isLoading}

            <div className="flex items-center justify-center h-full">              className="flex-1 resize-none border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50"

              <div className="text-center max-w-md">              rows={1}

                <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded-full inline-block mb-4">              style={{

                  <Bot size={32} className="text-blue-600 dark:text-blue-400" />                minHeight: '44px',

                </div>                maxHeight: '120px',

                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">              }}

                  Welcome to Perfect ChatGPT Clone            />

                </h2>            <button

                <p className="text-gray-600 dark:text-gray-400 mb-4">              onClick={sendMessage}

                  Start a conversation with AI. Ask anything!              disabled={!inputText.trim() || isLoading}

                </p>              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"

                <div className="text-sm text-gray-500 dark:text-gray-500 space-y-1">            >

                  <p>• Real AI responses</p>              {isLoading ? (

                  <p>• Conversation memory</p>                <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />

                  <p>• Code highlighting</p>              ) : (

                  <p>• Markdown support</p>                <Send size={20} />

                </div>              )}

              </div>              {isLoading ? 'Sending...' : 'Send'}

            </div>            </button>

          ) : (          </div>

            <div className="space-y-6 p-6">        </div>

              {messages.map((message) => (      </div>

                <div    </div>

                  key={message.id}  );

                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}}
                >
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                    message.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                  }`}>
                    {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  
                  {/* Message Content */}
                  <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block p-4 rounded-xl ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-800'
                    }`}>
                      {message.role === 'user' ? (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      ) : (
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          <ReactMarkdown components={PerfectMarkdownComponents}>
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Perfect Streaming Message */}
              {streamingContent && (
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
                    <Bot size={16} className="text-gray-600 dark:text-gray-400" />
                  </div>
                  <div className="flex-1 max-w-3xl">
                    <div className="inline-block p-4 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown components={PerfectMarkdownComponents}>
                          {streamingContent}
                        </ReactMarkdown>
                      </div>
                      <div className="mt-3 flex items-center gap-2 text-blue-500">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium">AI is typing...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Perfect Error Display */}
        {error && (
          <div className="mx-6 mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium">Error: {error}</span>
            </div>
          </div>
        )}

        {/* Perfect Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                disabled={isLoading || !isConnected}
                className="w-full resize-none border border-gray-300 dark:border-gray-700 rounded-xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                rows={1}
                style={{
                  minHeight: '50px',
                  maxHeight: '120px',
                }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputText.trim() || isLoading || !isConnected}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl transition-colors font-medium flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send size={16} />
                  <span>Send</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}