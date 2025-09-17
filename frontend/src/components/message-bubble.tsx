'use client'

import { Message } from '@/types/chat'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { User, Bot, Search, Zap, Brain } from 'lucide-react'
import { cn } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'

interface MessageBubbleProps {
  message: Message
  isStreaming?: boolean
}

export default function MessageBubble({ message, isStreaming = false }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={cn(
      "flex gap-3 max-w-4xl",
      isUser ? "ml-auto flex-row-reverse" : "mr-auto"
    )}>
      {/* Avatar */}
      <Avatar className={cn(
        "w-8 h-8 flex-shrink-0",
        isUser ? "bg-blue-500" : "bg-gradient-to-r from-purple-500 to-blue-600"
      )}>
        <AvatarFallback className="text-white">
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </AvatarFallback>
      </Avatar>

      {/* Message Content */}
      <div className={cn(
        "flex flex-col gap-2 max-w-[85%]",
        isUser && "items-end"
      )}>
        {/* Message Bubble */}
        <div className={cn(
          "px-4 py-3 rounded-2xl shadow-sm",
          isUser 
            ? "bg-blue-500 text-white" 
            : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700",
          isStreaming && "animate-pulse"
        )}>
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code({children, className, ...props}) {
                    const match = /language-(\w+)/.exec(className || '')
                    return (
                      <code className={cn("bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm", className)} {...props}>
                        {children}
                      </code>
                    )
                  },
                  pre({children}) {
                    return (
                      <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto">
                        {children}
                      </pre>
                    )
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
          
          {isStreaming && (
            <div className="mt-2 flex items-center gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          )}
        </div>

        {/* Metadata for AI messages */}
        {!isUser && message.metadata && (
          <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 px-2">
            {message.metadata.ragEnhanced && (
              <div className="flex items-center gap-1">
                <Search className="w-3 h-3" />
                <span>Real-time search</span>
              </div>
            )}
            {message.metadata.toolsUsed && message.metadata.toolsUsed.length > 0 && (
              <div className="flex items-center gap-1">
                <Zap className="w-3 h-3" />
                <span>{message.metadata.toolsUsed.length} tools</span>
              </div>
            )}
            {message.metadata.workflowConfidence && (
              <div className="flex items-center gap-1">
                <Brain className="w-3 h-3" />
                <span>{Math.round(message.metadata.workflowConfidence * 100)}% confidence</span>
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className={cn(
          "text-xs text-gray-500 dark:text-gray-400 px-2",
          isUser && "text-right"
        )}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}