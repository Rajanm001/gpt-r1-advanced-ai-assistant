'use client'

import { create } from 'zustand'

interface ConversationStore {
  currentConversationId: number | null
  conversations: Array<{
    id: number
    title: string
    updated_at: string
  }>
  setCurrentConversation: (id: number) => void
  addConversation: (conversation: { id: number; title: string; updated_at: string }) => void
  updateConversation: (id: number, updates: Partial<{ title: string; updated_at: string }>) => void
  deleteConversation: (id: number) => void
  clearConversations: () => void
}

export const useConversationStore = create<ConversationStore>((set, get) => ({
  currentConversationId: null,
  conversations: [],
  
  setCurrentConversation: (id: number) => {
    set({ currentConversationId: id })
  },
  
  addConversation: (conversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      currentConversationId: conversation.id
    }))
  },
  
  updateConversation: (id, updates) => {
    set((state) => ({
      conversations: state.conversations.map(conv =>
        conv.id === id ? { ...conv, ...updates } : conv
      )
    }))
  },
  
  deleteConversation: (id) => {
    set((state) => ({
      conversations: state.conversations.filter(conv => conv.id !== id),
      currentConversationId: state.currentConversationId === id ? null : state.currentConversationId
    }))
  },
  
  clearConversations: () => {
    set({ conversations: [], currentConversationId: null })
  }
}))