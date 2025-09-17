'use client'

import { useState, useEffect } from 'react'
import { MessageSquare, Plus, Settings, Moon, Sun, LogOut, Trash2, Edit2, Check, X } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useConversationStore } from '@/store/conversation'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/lib/utils'

interface Conversation {
  id: number
  title: string
  updated_at: string
}

export default function ConversationSidebar() {
  const { theme, setTheme } = useTheme()
  const { 
    conversations, 
    currentConversationId, 
    setCurrentConversation,
    addConversation,
    updateConversation,
    deleteConversation,
    clearConversations
  } = useConversationStore()
  const { user, logout, token } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTitle, setEditTitle] = useState('')

  // Load conversations on mount
  useEffect(() => {
    if (token) {
      loadConversations()
    }
  }, [token])

  const loadConversations = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        // Clear and reload conversations
        clearConversations()
        data.forEach((conv: Conversation) => addConversation(conv))
      }
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: 'New Chat'
        })
      })
      
      if (response.ok) {
        const newConversation = await response.json()
        addConversation(newConversation)
        setCurrentConversation(newConversation.id)
      }
    } catch (error) {
      console.error('Failed to create conversation:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleConversationSelect = (conversation: Conversation) => {
    setCurrentConversation(conversation.id)
  }

  const handleEditStart = (conversation: Conversation) => {
    setEditingId(conversation.id)
    setEditTitle(conversation.title)
  }

  const handleEditSave = async (conversationId: number) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${conversationId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: editTitle
        })
      })
      
      if (response.ok) {
        updateConversation(conversationId, { title: editTitle })
        setEditingId(null)
        setEditTitle('')
      }
    } catch (error) {
      console.error('Failed to update conversation:', error)
    }
  }

  const handleEditCancel = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const handleDelete = async (conversationId: number) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        deleteConversation(conversationId)
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) return 'Today'
    if (diffDays === 2) return 'Yesterday'
    if (diffDays <= 7) return `${diffDays} days ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="flex flex-col h-full bg-muted/20 dark:bg-gray-900">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <button
          onClick={handleNewChat}
          disabled={isLoading}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border border-border hover:bg-accent transition-colors disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        <div className="space-y-1">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={cn(
                "group w-full text-left p-3 rounded-lg transition-colors hover:bg-accent",
                currentConversationId === conversation.id ? "bg-accent" : ""
              )}
            >
              <div className="flex items-start gap-2">
                <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0" onClick={() => handleConversationSelect(conversation)}>
                  {editingId === conversation.id ? (
                    <div className="flex gap-1">
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className="flex-1 text-sm bg-background border rounded px-2 py-1"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleEditSave(conversation.id)
                          if (e.key === 'Escape') handleEditCancel()
                        }}
                        autoFocus
                      />
                      <button
                        onClick={() => handleEditSave(conversation.id)}
                        className="p-1 text-green-600 hover:bg-green-100 rounded"
                      >
                        <Check className="w-3 h-3" />
                      </button>
                      <button
                        onClick={handleEditCancel}
                        className="p-1 text-red-600 hover:bg-red-100 rounded"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="font-medium text-sm cursor-pointer">
                        {conversation.title || 'Untitled Chat'}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {formatDate(conversation.updated_at)}
                      </div>
                    </>
                  )}
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEditStart(conversation)
                    }}
                    className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                  >
                    <Edit2 className="w-3 h-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(conversation.id)
                    }}
                    className="p-1 text-red-500 hover:text-red-700 hover:bg-red-100 rounded"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          {conversations.length === 0 && !isLoading && (
            <div className="text-center text-muted-foreground text-sm p-4">
              No conversations yet. Start a new chat!
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-medium">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="truncate">{user?.username || 'User'}</span>
          </div>
          
          <div className="flex gap-1">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-1.5 rounded-lg hover:bg-accent transition-colors"
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <button
              onClick={logout}
              className="p-1.5 rounded-lg hover:bg-accent transition-colors text-red-500"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}