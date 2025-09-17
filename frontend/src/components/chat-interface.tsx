'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, AlertCircle, Wifi, WifiOff, RefreshCw } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/lib/api'
import { cn, formatTime } from '@/lib/utils'
import { StreamMessage, Message } from '@/types'
import toast from 'react-hot-toast'

// Enhanced error types for production-ready UI
interface ErrorState {
  type: 'api_error' | 'network_error' | 'validation_error' | 'fallback_active' | null
  message: string
  canRetry: boolean
  severity: 'low' | 'medium' | 'high'
}

// Progressive typing state
interface TypingState {
  isTyping: boolean
  currentText: string
  fullText: string
  chunkId: number
}

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const [useRAG, setUseRAG] = useState(false)
  const [errorState, setErrorState] = useState<ErrorState>({ type: null, message: '', canRetry: false, severity: 'low' })
  const [typingState, setTypingState] = useState<TypingState>({
    isTyping: false,
    currentText: '',
    fullText: '',
    chunkId: 0
  })
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connected')
  const [retryCount, setRetryCount] = useState(0)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  
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
  }, [currentConversation?.messages, typingState.currentText])

  // Enhanced smooth scroll with animation
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'end',
      inline: 'nearest'
    })
  }

  // Clear error state when user starts typing
  useEffect(() => {
    if (message.trim() && errorState.type) {
      setErrorState({ type: null, message: '', canRetry: false, severity: 'low' })
    }
  }, [message])

  // Enhanced error handling with user-friendly messages
  const handleError = (error: any, context: string) => {
    console.error(`Error in ${context}:`, error)
    
    let errorInfo: ErrorState = {
      type: 'api_error',
      message: 'Something went wrong. Please try again.',
      canRetry: true,
      severity: 'medium'
    }

    if (error.name === 'AbortError') {
      return // User cancelled, don't show error
    }

    if (error.message?.includes('network') || error.message?.includes('fetch')) {
      errorInfo = {
        type: 'network_error',
        message: 'Connection lost. Please check your internet and try again.',
        canRetry: true,
        severity: 'high'
      }
      setConnectionStatus('disconnected')
    } else if (error.status === 400) {
      errorInfo = {
        type: 'validation_error',
        message: 'Please check your message and try again.',
        canRetry: false,
        severity: 'low'
      }
    } else if (error.status === 429) {
      errorInfo = {
        type: 'api_error',
        message: 'Too many requests. Please wait a moment before trying again.',
        canRetry: true,
        severity: 'medium'
      }
    } else if (error.status >= 500) {
      errorInfo = {
        type: 'api_error',
        message: 'Server is temporarily unavailable. We\'re working on it!',
        canRetry: true,
        severity: 'high'
      }
    }

    setErrorState(errorInfo)
    toast.error(errorInfo.message)
  }

  // Progressive typing animation for incoming messages
  const animateTyping = (newText: string, chunkId: number, isFallback = false) => {
    setTypingState(prev => {
      if (chunkId === 1) {
        // New message starting
        return {
          isTyping: true,
          currentText: newText,
          fullText: newText,
          chunkId: 1
        }
      } else {
        // Continuing message
        const updatedText = prev.fullText + newText
        return {
          ...prev,
          currentText: updatedText,
          fullText: updatedText,
          chunkId
        }
      }
    })

    // Add slight delay for typing effect
    if (!isFallback) {
      setTimeout(scrollToBottom, 50)
    }
  }

  // Enhanced retry mechanism
  const retryRequest = async () => {
    if (retryCount >= 3) {
      setErrorState({
        type: 'api_error',
        message: 'Maximum retry attempts reached. Please try again later.',
        canRetry: false,
        severity: 'high'
      })
      return
    }

    setRetryCount(prev => prev + 1)
    setErrorState({ type: null, message: '', canRetry: false, severity: 'low' })
    
    // Re-submit the last message
    const lastUserMessage = currentConversation?.messages
      ?.filter(m => m.role === 'user')
      ?.slice(-1)[0]

    if (lastUserMessage) {
      await submitMessage(lastUserMessage.content, true)
    }
  }

  // Enhanced submit handler with comprehensive error handling
  const submitMessage = async (messageText: string, isRetry = false) => {
    if (!messageText.trim() || isStreaming) return

    // Reset states for new message
    setErrorState({ type: null, message: '', canRetry: false, severity: 'low' })
    setConnectionStatus('connecting')
    setTypingState({ isTyping: false, currentText: '', fullText: '', chunkId: 0 })
    
    if (!isRetry) {
      setRetryCount(0)
    }

    try {
      let conversationId = currentConversation?.id

      // Create conversation if none exists
      if (!conversationId) {
        const newConversation = await createConversation(messageText)
        conversationId = newConversation.id
      }

      // Add user message to UI immediately
      if (!isRetry) {
        addMessage({
          id: Date.now(),
          conversation_id: conversationId,
          role: 'user',
          content: messageText,
          timestamp: new Date().toISOString()
        })
      }

      setStreaming(true)
      setConnectionStatus('connected')

      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController()

      // Stream response with enhanced error handling
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          message: messageText,
          conversation_id: conversationId,
          use_rag: useRAG
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Response stream not available')
      }

      let assistantMessage = ''
      let messageId = Date.now() + 1
      let chunkCount = 0
      let hasError = false

      // Process streaming response
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              switch (data.type) {
                case 'metadata':
                  console.log('Stream started:', data)
                  break
                
                case 'search_context':
                  toast.success('Enhanced with web search results', { duration: 2000 })
                  break
                
                case 'content':
                  chunkCount++
                  assistantMessage += data.content
                  animateTyping(data.content, data.chunk_id, data.fallback)
                  
                  // Update message in store
                  if (chunkCount === 1) {
                    addMessage({
                      id: messageId,
                      conversation_id: conversationId!,
                      role: 'assistant',
                      content: assistantMessage,
                      timestamp: new Date().toISOString()
                    })
                  } else {
                    updateLastMessage(assistantMessage)
                  }
                  break
                
                case 'api_error':
                  hasError = true
                  console.warn('API Error:', data.error_info)
                  if (data.error_info.fallback_available) {
                    toast.warning('Using intelligent fallback response', { duration: 3000 })
                    setErrorState({
                      type: 'fallback_active',
                      message: 'AI service temporarily unavailable - using fallback response',
                      canRetry: true,
                      severity: 'low'
                    })
                  }
                  break
                
                case 'warning':
                  toast.warning(data.message, { duration: 3000 })
                  break
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError)
            }
          }
        }
      }

      // Final cleanup
      setTypingState(prev => ({ ...prev, isTyping: false }))
      
      if (!hasError) {
        setConnectionStatus('connected')
        toast.success('Message sent successfully', { duration: 1000 })
      }

    } catch (error: any) {
      handleError(error, 'message submission')
    } finally {
      setStreaming(false)
      setTypingState(prev => ({ ...prev, isTyping: false }))
      abortControllerRef.current = null
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isStreaming) return

    const messageText = message.trim()
    setMessage('')
    await submitMessage(messageText)
  }

  // Cancel current request
  const cancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setStreaming(false)
      setTypingState({ isTyping: false, currentText: '', fullText: '', chunkId: 0 })
      toast.info('Request cancelled')
    }
  }

  // Enhanced message rendering with error states
  const renderMessage = (msg: Message, index: number) => {
    const isLast = index === (currentConversation?.messages?.length || 0) - 1
    const isAssistant = msg.role === 'assistant'
    const isTyping = isLast && isAssistant && typingState.isTyping
    const displayContent = isTyping ? typingState.currentText : msg.content

    return (
      <div
        key={msg.id}
        className={cn(
          'flex gap-3 p-4 transition-all duration-200',
          isAssistant ? 'bg-gray-50 dark:bg-gray-800/50' : 'bg-white dark:bg-gray-900'
        )}
      >
        <div className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isAssistant 
            ? 'bg-blue-500 text-white' 
            : 'bg-green-500 text-white'
        )}>
          {isAssistant ? <Bot size={16} /> : <User size={16} />}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-sm">
              {isAssistant ? 'GPT.R1' : 'You'}
            </span>
            <span className="text-xs text-gray-500">
              {formatTime(msg.timestamp)}
            </span>
            {isTyping && (
              <div className="flex items-center gap-1 text-blue-500">
                <Loader2 size={12} className="animate-spin" />
                <span className="text-xs">typing...</span>
              </div>
            )}
          </div>
          
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
              {displayContent}
            </ReactMarkdown>
          </div>
          
          {/* Typing cursor effect */}
          {isTyping && (
            <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1" />
          )}
        </div>
      </div>
    )
  }

  // Connection status indicator
  const ConnectionIndicator = () => (
    <div className={cn(
      'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium',
      connectionStatus === 'connected' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
      connectionStatus === 'connecting' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
      'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    )}>
      {connectionStatus === 'connected' ? <Wifi size={12} /> :
       connectionStatus === 'connecting' ? <Loader2 size={12} className="animate-spin" /> :
       <WifiOff size={12} />}
      {connectionStatus === 'connected' ? 'Connected' :
       connectionStatus === 'connecting' ? 'Connecting...' :
       'Disconnected'}
    </div>
  )

  // Error banner component
  const ErrorBanner = () => {
    if (!errorState.type) return null

    return (
      <div className={cn(
        'flex items-center justify-between p-3 rounded-lg border-l-4 mb-4',
        errorState.severity === 'low' ? 'bg-blue-50 border-blue-400 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200' :
        errorState.severity === 'medium' ? 'bg-yellow-50 border-yellow-400 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200' :
        'bg-red-50 border-red-400 text-red-800 dark:bg-red-900/20 dark:text-red-200'
      )}>
        <div className="flex items-center gap-3">
          <AlertCircle size={16} />
          <span className="text-sm font-medium">{errorState.message}</span>
        </div>
        
        {errorState.canRetry && (
          <button
            onClick={retryRequest}
            className="flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-md hover:bg-white/20 transition-colors"
          >
            <RefreshCw size={12} />
            Retry {retryCount > 0 && `(${retryCount}/3)`}
          </button>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header with connection status */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              GPT.R1 Chat
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              AI Assistant with Web Search
            </p>
          </div>
          <ConnectionIndicator />
        </div>
      </div>

      {/* Error banner */}
      <div className="flex-shrink-0 px-4 pt-4">
        <ErrorBanner />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {currentConversation?.messages?.length ? (
          <>
            {currentConversation.messages.map((msg, index) => 
              renderMessage(msg, index)
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center max-w-md">
              <Bot size={48} className="mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Welcome to GPT.R1
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Start a conversation by typing a message below. 
                Enable web search for enhanced responses with real-time information.
              </p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Enhanced input form */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* RAG toggle */}
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <input
                type="checkbox"
                checked={useRAG}
                onChange={(e) => setUseRAG(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                disabled={isStreaming}
              />
              Enable web search for enhanced responses
            </label>
          </div>

          {/* Message input */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
                placeholder="Type your message... (Shift+Enter for new line)"
                rows={1}
                className="w-full resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 pr-12 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                style={{
                  minHeight: '50px',
                  maxHeight: '150px',
                  height: 'auto'
                }}
                disabled={isStreaming}
              />
              
              {/* Character count */}
              <div className="absolute bottom-1 right-1 text-xs text-gray-400">
                {message.length}/4000
              </div>
            </div>

            {/* Send/Cancel button */}
            <button
              type={isStreaming ? 'button' : 'submit'}
              onClick={isStreaming ? cancelRequest : undefined}
              disabled={(!message.trim() && !isStreaming) || connectionStatus === 'disconnected'}
              className={cn(
                'flex-shrink-0 px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2',
                isStreaming
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed'
              )}
            >
              {isStreaming ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Cancel
                </>
              ) : (
                <>
                  <Send size={16} />
                  Send
                </>
              )}
            </button>
          </div>

          {/* Status indicators */}
          {isStreaming && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 size={14} className="animate-spin" />
              <span>
                {typingState.isTyping ? 'GPT.R1 is typing...' : 'Processing your message...'}
              </span>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}