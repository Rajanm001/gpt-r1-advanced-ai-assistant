'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/lib/api'
import { cn, formatTime } from '@/lib/utils'
import { StreamMessage, Message } from '@/types'
import toast from 'react-hot-toast'

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const [useRAG, setUseRAG] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const {
    currentConversation,
    isStreaming,
    addMessage,
    updateLastMessage,
    setStreaming,
    createConversation
  } = useChatStore()
  
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    scrollToBottom()
  }, [currentConversation?.messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isStreaming) return

    const userMessage = message.trim()
    setMessage('')
    
    try {
      let conversationId = currentConversation?.id

      // Create conversation if none exists
      if (!conversationId) {
        const newConversation = await createConversation()
        conversationId = newConversation.id
      }

      // Add user message to UI
      const newUserMessage: Message = {
        id: Date.now(),
        conversation_id: conversationId,
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      }
      addMessage(newUserMessage)

      // Add placeholder assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        conversation_id: conversationId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString()
      }
      addMessage(assistantMessage)

      setStreaming(true)

      // Start streaming
      const response = await apiClient.createChatStream({
        message: userMessage,
        conversation_id: conversationId,
        use_rag: useRAG
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value)
            const lines = chunk.split('\n')

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data: StreamMessage = JSON.parse(line.slice(6))
                  
                  switch (data.type) {
                    case 'content':
                      if (data.content) {
                        updateLastMessage(data.content)
                      }
                      break
                    case 'context':
                      if (data.content) {
                        toast.success('Using web search for enhanced response')
                      }
                      break
                    case 'done':
                      setStreaming(false)
                      break
                    case 'error':
                      toast.error(data.content || 'An error occurred')
                      setStreaming(false)
                      break
                  }
                } catch (parseError) {
                  console.error('Failed to parse SSE data:', parseError)
                }
              }
            }
          }
        } finally {
          reader.releaseLock()
        }
      }
    } catch (error) {
      console.error('Chat error:', error)
      toast.error('Failed to send message')
      setStreaming(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Welcome to ChatGPT Clone</h2>
          <p className="text-muted-foreground">Please log in to start chatting</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
        {currentConversation?.messages.length === 0 && (
          <div className="text-center text-muted-foreground py-8">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start a conversation by sending a message below.</p>
            {useRAG && (
              <p className="text-sm mt-2 text-primary">
                RAG mode enabled - I'll search the web for additional context
              </p>
            )}
          </div>
        )}
        
        {currentConversation?.messages.map((msg, index) => (
          <div
            key={msg.id}
            className={cn(
              "flex gap-3 message-enter",
              msg.role === 'user' ? "justify-end" : "justify-start"
            )}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-primary-foreground" />
              </div>
            )}
            
            <div
              className={cn(
                "max-w-3xl rounded-lg px-4 py-2",
                msg.role === 'user'
                  ? "bg-primary text-primary-foreground ml-12"
                  : "bg-muted"
              )}
            >
              {msg.role === 'assistant' ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '')
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={oneDark}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        )
                      }
                    }}
                  >
                    {msg.content || ''}
                  </ReactMarkdown>
                  {isStreaming && index === currentConversation.messages.length - 1 && (
                    <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
                  )}
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}
              
              <div className="text-xs opacity-60 mt-1">
                {formatTime(msg.timestamp)}
              </div>
            </div>
            
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-background p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="w-full resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 min-h-[40px] max-h-32"
              rows={1}
              disabled={isStreaming}
            />
          </div>
          
          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={() => setUseRAG(!useRAG)}
              className={cn(
                "px-3 py-1 text-xs rounded border transition-colors",
                useRAG
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-background text-muted-foreground border-border hover:bg-muted"
              )}
            >
              RAG
            </button>
            
            <button
              type="submit"
              disabled={!message.trim() || isStreaming}
              className="p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isStreaming ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}