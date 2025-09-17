'use client'

import { useState, useEffect, useRef } from 'react'
import { Message, StreamResponse, ChatState } from '@/types/chat'
import { useAuthStore } from '@/store/auth'
import { useConversationStore } from '@/store/conversation'
import MessageBubble from './message-bubble'
import StreamingIndicator from './streaming-indicator'
import ChatInput from './chat-input'
import { Loader2, Zap, Search, Brain } from 'lucide-react'

export default function EnhancedChatInterface() {
  const { token } = useAuthStore()
  const { currentConversationId } = useConversationStore()
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    isTyping: false,
    streamingMessage: '',
    currentStep: '',
    ragStatus: {
      analyzing: false,
      searchUsed: false,
      enhanced: false
    }
  })
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatState.messages, chatState.streamingMessage])

  const sendMessage = async (content: string) => {
    if (!content.trim() || !currentConversationId || chatState.isLoading) return

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date().toISOString()
    }

    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      isTyping: false,
      streamingMessage: '',
      currentStep: '',
      ragStatus: { analyzing: false, searchUsed: false, enhanced: false }
    }))

    // Prepare assistant message
    const assistantMessageId = (Date.now() + 1).toString()
    let fullResponse = ''
    let messageMetadata = {}

    try {
      // Create abort controller for this request
      abortControllerRef.current = new AbortController()

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          conversation_id: currentConversationId,
          message: content
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamResponse = JSON.parse(line.slice(6))
              
              switch (data.type) {
                case 'rag_start':
                  setChatState(prev => ({
                    ...prev,
                    ragStatus: { ...prev.ragStatus, analyzing: true },
                    currentStep: '🔍 Analyzing for real-time information...'
                  }))
                  break

                case 'rag_complete':
                  setChatState(prev => ({
                    ...prev,
                    ragStatus: {
                      analyzing: false,
                      searchUsed: data.search_used || false,
                      enhanced: data.search_used || false
                    },
                    currentStep: data.search_used ? 
                      '✅ Enhanced with search results' : 
                      '📚 Using knowledge base'
                  }))
                  messageMetadata = { 
                    ...messageMetadata, 
                    ragEnhanced: data.search_used 
                  }
                  break

                case 'workflow_start':
                  setChatState(prev => ({
                    ...prev,
                    currentStep: '🤖 Processing with AI agents...'
                  }))
                  break

                case 'response_start':
                  setChatState(prev => ({
                    ...prev,
                    isTyping: true,
                    currentStep: '📝 Generating response...'
                  }))
                  messageMetadata = {
                    ...messageMetadata,
                    toolsUsed: data.tools_used,
                    workflowConfidence: data.workflow_confidence
                  }
                  break

                case 'content':
                  if (data.content) {
                    fullResponse += data.content
                    setChatState(prev => ({
                      ...prev,
                      streamingMessage: fullResponse
                    }))
                  }
                  break

                case 'complete':
                  const assistantMessage: Message = {
                    id: assistantMessageId,
                    content: fullResponse,
                    role: 'assistant',
                    timestamp: new Date().toISOString(),
                    metadata: messageMetadata
                  }

                  setChatState(prev => ({
                    ...prev,
                    messages: [...prev.messages, assistantMessage],
                    isLoading: false,
                    isTyping: false,
                    streamingMessage: '',
                    currentStep: '',
                    ragStatus: { analyzing: false, searchUsed: false, enhanced: false }
                  }))
                  break

                case 'error':
                  throw new Error(data.message || 'Stream error occurred')
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', parseError)
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Request aborted')
        return
      }

      console.error('Chat error:', error)
      setChatState(prev => ({
        ...prev,
        isLoading: false,
        isTyping: false,
        streamingMessage: '',
        currentStep: '',
        ragStatus: { analyzing: false, searchUsed: false, enhanced: false },
        messages: [...prev.messages, {
          id: assistantMessageId,
          content: '❌ Sorry, I encountered an error. Please try again.',
          role: 'assistant',
          timestamp: new Date().toISOString()
        }]
      }))
    }
  }

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setChatState(prev => ({
        ...prev,
        isLoading: false,
        isTyping: false,
        streamingMessage: '',
        currentStep: '',
        ragStatus: { analyzing: false, searchUsed: false, enhanced: false }
      }))
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatState.messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
              AI Assistant with RAG
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-md">
              Ask me anything! I can search the internet for real-time information and use advanced AI tools to help you.
            </p>
            <div className="flex items-center gap-4 mt-6 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                Real-time search
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                AI tools
              </div>
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Smart responses
              </div>
            </div>
          </div>
        )}

        {chatState.messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Streaming Message */}
        {chatState.isLoading && (
          <div className="space-y-3">
            <StreamingIndicator 
              step={chatState.currentStep}
              ragStatus={chatState.ragStatus}
              isTyping={chatState.isTyping}
            />
            
            {chatState.streamingMessage && (
              <MessageBubble 
                message={{
                  id: 'streaming',
                  content: chatState.streamingMessage,
                  role: 'assistant',
                  timestamp: new Date().toISOString()
                }}
                isStreaming={true}
              />
            )}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <ChatInput 
          onSendMessage={sendMessage}
          isLoading={chatState.isLoading}
          onStop={stopGeneration}
        />
      </div>
    </div>
  )
}