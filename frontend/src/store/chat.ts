import { create } from 'zustand'
import { ChatStore, Conversation, Message } from '@/types'
import { apiClient } from '@/lib/api'
import { generateConversationTitle } from '@/lib/utils'
import toast from 'react-hot-toast'

export const useChatStore = create<ChatStore>()((set, get) => ({
  conversations: [],
  currentConversation: null,
  isLoading: false,
  isStreaming: false,
  error: null,

  setConversations: (conversations: Conversation[]) => {
    set({ conversations })
  },

  setCurrentConversation: (conversation: Conversation | null) => {
    set({ currentConversation: conversation })
  },

  addMessage: (message: Message) => {
    const { currentConversation, conversations } = get()
    
    if (currentConversation && currentConversation.id === message.conversation_id) {
      const updatedConversation = {
        ...currentConversation,
        messages: [...currentConversation.messages, message]
      }
      
      const updatedConversations = conversations.map(conv =>
        conv.id === message.conversation_id ? updatedConversation : conv
      )
      
      set({
        currentConversation: updatedConversation,
        conversations: updatedConversations
      })
    }
  },

  updateLastMessage: (content: string) => {
    const { currentConversation, conversations } = get()
    
    if (currentConversation && currentConversation.messages.length > 0) {
      const messages = [...currentConversation.messages]
      const lastMessage = messages[messages.length - 1]
      
      if (lastMessage.role === 'assistant') {
        lastMessage.content += content
        
        const updatedConversation = {
          ...currentConversation,
          messages
        }
        
        const updatedConversations = conversations.map(conv =>
          conv.id === currentConversation.id ? updatedConversation : conv
        )
        
        set({
          currentConversation: updatedConversation,
          conversations: updatedConversations
        })
      }
    }
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading })
  },

  setStreaming: (streaming: boolean) => {
    set({ isStreaming: streaming })
  },

  setError: (error: string | null) => {
    set({ error })
  },

  createConversation: async (title?: string) => {
    try {
      set({ isLoading: true })
      
      const conversation = await apiClient.createConversation(title)
      const { conversations } = get()
      
      set({
        conversations: [conversation, ...conversations],
        currentConversation: conversation,
        isLoading: false
      })
      
      return conversation
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create conversation'
      toast.error(message)
      set({ isLoading: false, error: message })
      throw error
    }
  },

  loadConversations: async () => {
    try {
      set({ isLoading: true })
      const conversations = await apiClient.getConversations()
      set({ conversations, isLoading: false })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to load conversations'
      set({ error: message, isLoading: false })
      toast.error(message)
    }
  },

  loadConversation: async (id: number) => {
    try {
      set({ isLoading: true })
      const conversation = await apiClient.getConversation(id)
      set({ currentConversation: conversation, isLoading: false })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to load conversation'
      set({ error: message, isLoading: false })
      toast.error(message)
    }
  },
}))