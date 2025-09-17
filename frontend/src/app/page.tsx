'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import EnhancedChatInterface from '@/components/enhanced-chat-interface'
import EnhancedConversationSidebar from '@/components/enhanced-conversation-sidebar'
import Header from '@/components/header'
import AuthModal from '@/components/auth-modal'

export default function HomePage() {
  const { isAuthenticated, token } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    // Initialize auth state from cookie if exists
    if (typeof window !== 'undefined') {
      const savedToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('auth_token='))
        ?.split('=')[1]
      
      if (savedToken && !token) {
        useAuthStore.getState().setToken(savedToken)
      }
    }
  }, [token])

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-80 border-r border-border flex-shrink-0">
        <EnhancedConversationSidebar />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <Header />
        <div className="flex-1">
          {isAuthenticated ? <EnhancedChatInterface /> : <AuthModal />}
        </div>
      </div>
    </div>
  )
}