'use client';

import { Bot, User, Clock, Search, Copy, ThumbsUp, ThumbsDown, MoreHorizontal } from 'lucide-react';
import { Message } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from 'react';

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export default function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const formatTime = (date: Date) => {
    return formatDistanceToNow(date, { addSuffix: true });
  };

  return (
    <div 
      className={`flex items-start space-x-4 message-bubble group ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border ${
        isUser 
          ? 'bg-blue-500/20 border-blue-400/30' 
          : 'bg-green-500/20 border-green-400/30'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-blue-400" />
        ) : (
          <Bot className={`w-5 h-5 text-green-400 ${isStreaming ? 'animate-pulse' : ''}`} />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-4xl ${isUser ? 'flex flex-col items-end' : ''}`}>
        <div className={`modern-card rounded-2xl px-6 py-4 relative ${
          isUser 
            ? 'bg-blue-500/10 border-blue-400/30' 
            : 'bg-gray-800/50 border-gray-600/50'
        }`}>
          {/* Message header */}
          <div className={`flex items-center justify-between mb-2 ${isUser ? 'flex-row-reverse' : ''}`}>
            <div className={`flex items-center space-x-2 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <span className={`font-semibold ${isUser ? 'text-blue-400' : 'text-green-400'}`}>
                {isUser ? 'You' : 'AI Assistant'}
              </span>
              {!isUser && message.id === -1 && (
                <div className="flex items-center space-x-1 text-xs text-green-400">
                  <Search className="h-3 w-3" />
                  <span>Enhanced Mode</span>
                </div>
              )}
              {isStreaming && (
                <div className="flex items-center space-x-1 text-xs text-green-400">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>Generating...</span>
                </div>
              )}
            </div>
            
            {/* Actions */}
            <div className={`flex items-center space-x-1 transition-opacity ${
              showActions ? 'opacity-100' : 'opacity-0'
            }`}>
              <button
                onClick={handleCopy}
                className="p-1 hover:bg-gray-600/50 rounded text-gray-400 hover:text-white transition-colors"
                title="Copy message"
              >
                <Copy className="h-3 w-3" />
              </button>
              {!isUser && (
                <>
                  <button
                    className="p-1 hover:bg-gray-600/50 rounded text-gray-400 hover:text-green-400 transition-colors"
                    title="Good response"
                  >
                    <ThumbsUp className="h-3 w-3" />
                  </button>
                  <button
                    className="p-1 hover:bg-gray-600/50 rounded text-gray-400 hover:text-red-400 transition-colors"
                    title="Poor response"
                  >
                    <ThumbsDown className="h-3 w-3" />
                  </button>
                </>
              )}
              <button
                className="p-1 hover:bg-gray-600/50 rounded text-gray-400 hover:text-white transition-colors"
                title="More options"
              >
                <MoreHorizontal className="h-3 w-3" />
              </button>
            </div>
          </div>

          {/* Message content */}
          <div className={`prose prose-invert max-w-none ${
            isUser ? 'text-right' : ''
          }`}>
            {isUser ? (
              <div className="text-white whitespace-pre-wrap break-words">
                {message.content}
              </div>
            ) : (
              <ReactMarkdown
                className="markdown-content"
                components={{
                  code({ className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const language = match ? match[1] : '';
                    const isCodeBlock = language && children && typeof children === 'string' && children.includes('\n');

                    return isCodeBlock ? (
                      <div className="relative">
                        <div className="flex items-center justify-between bg-gray-900 px-4 py-2 rounded-t-lg border border-gray-600">
                          <span className="text-xs text-gray-400">{language}</span>
                          <button
                            onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                            className="text-xs text-gray-400 hover:text-white transition-colors"
                          >
                            Copy
                          </button>
                        </div>
                        <SyntaxHighlighter
                          style={oneDark as any}
                          language={language}
                          PreTag="div"
                          className="rounded-b-lg border-x border-b border-gray-600"
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <code
                        className="bg-gray-700 px-2 py-1 rounded text-green-400 text-sm"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                  p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
                  ul: ({ children }) => <ul className="mb-4 space-y-1 list-disc list-inside">{children}</ul>,
                  ol: ({ children }) => <ol className="mb-4 space-y-1 list-decimal list-inside">{children}</ol>,
                  li: ({ children }) => <li className="text-gray-200">{children}</li>,
                  h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 text-white">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-xl font-bold mb-3 text-white">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-lg font-bold mb-2 text-white">{children}</h3>,
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-green-400 pl-4 py-2 bg-green-500/10 rounded-r-lg mb-4 italic">
                      {children}
                    </blockquote>
                  ),
                  a: ({ href, children }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 underline"
                    >
                      {children}
                    </a>
                  ),
                  table: ({ children }) => (
                    <div className="overflow-x-auto mb-4">
                      <table className="min-w-full border border-gray-600 rounded-lg">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="px-4 py-2 bg-gray-700 border-b border-gray-600 text-left font-semibold">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="px-4 py-2 border-b border-gray-600">
                      {children}
                    </td>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
            
            {/* Streaming cursor */}
            {isStreaming && (
              <span className="inline-block w-2 h-5 bg-green-400 animate-pulse ml-1"></span>
            )}
          </div>

          {/* Copy notification */}
          {copied && (
            <div className="absolute -top-2 right-4 bg-green-500 text-white text-xs px-2 py-1 rounded animate-bounce">
              Copied!
            </div>
          )}
        </div>

        {/* Timestamp */}
        <div className={`flex items-center space-x-2 mt-2 text-xs text-gray-500 ${
          isUser ? 'flex-row-reverse space-x-reverse' : ''
        }`}>
          <Clock className="h-3 w-3" />
          <span>{formatTime(timestamp)}</span>
        </div>
      </div>
    </div>
  );
}