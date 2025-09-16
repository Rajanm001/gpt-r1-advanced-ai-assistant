'use client'

import { useState } from 'react'
import { MessageSquare, Plus, Settings, Moon, Sun, LogOut } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { cn, formatDate, truncateText } from '@/lib/utils'

export default function ConversationSidebar() {
  const { theme, setTheme } = useTheme()
  const { 
    conversations, 
    currentConversation, 
    setCurrentConversation,
    createConversation,
    isLoading 
  } = useChatStore()
  const { user, logout } = useAuthStore()

  const handleNewChat = async () => {
    try {
      await createConversation('New Chat')
    } catch (error) {
      console.error('Failed to create conversation:', error)
    }
  }

  const handleConversationSelect = (conversation: any) => {
    setCurrentConversation(conversation)
  }

  return (
    <div className="flex flex-col h-full bg-muted/20">
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
            <button
              key={conversation.id}
              onClick={() => handleConversationSelect(conversation)}
              className={cn(
                "w-full text-left p-3 rounded-lg transition-colors hover:bg-accent",
                currentConversation?.id === conversation.id ? "bg-accent" : ""
              )}
            >
              <div className="flex items-start gap-2">
                <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">
                    {conversation.title || 'Untitled Chat'}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {formatDate(conversation.created_at)}
                  </div>
                  {conversation.messages.length > 0 && (
                    <div className="text-xs text-muted-foreground mt-1">
                      {truncateText(
                        conversation.messages[conversation.messages.length - 1]?.content || '',
                        50
                      )}
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
          
          {conversations.length === 0 && (
            <div className="text-center text-muted-foreground py-8 px-4">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new chat to begin</p>
            </div>
          )}
        </div>
      </div>

      {/* User Info & Settings */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center text-xs text-primary-foreground">
              {user?.username.charAt(0).toUpperCase()}
            </div>
            <span className="truncate">{user?.username}</span>
          </div>
          
          <div className="flex items-center gap-1">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-1.5 rounded hover:bg-accent"
              title="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </button>
            
            <button
              onClick={logout}
              className="p-1.5 rounded hover:bg-accent text-destructive"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div className="text-xs text-muted-foreground">
          ChatGPT Clone v1.0
        </div>
      </div>
    </div>
  )
}