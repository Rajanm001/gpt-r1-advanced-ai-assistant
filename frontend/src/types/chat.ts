interface StreamResponse {
  type: 'rag_start' | 'rag_complete' | 'workflow_start' | 'response_start' | 'content' | 'complete' | 'error'
  message?: string
  content?: string
  step?: string
  search_used?: boolean
  rag_enhanced?: boolean
  workflow_confidence?: number
  tools_used?: string[]
  timestamp?: string
}

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
  metadata?: {
    ragEnhanced?: boolean
    toolsUsed?: string[]
    workflowConfidence?: number
  }
}

interface ChatState {
  messages: Message[]
  isLoading: boolean
  isTyping: boolean
  streamingMessage: string
  currentStep: string
  ragStatus: {
    analyzing: boolean
    searchUsed: boolean
    enhanced: boolean
  }
}

export type { StreamResponse, Message, ChatState }