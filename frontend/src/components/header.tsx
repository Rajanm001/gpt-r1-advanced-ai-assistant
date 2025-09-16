'use client'

import { useState } from 'react'
import { Settings, HelpCircle, Github } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { useChatStore } from '@/store/chat'

export default function Header() {
  const { user } = useAuthStore()
  const { currentConversation } = useChatStore()

  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex items-center justify-between h-14 px-4">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">
            {currentConversation?.title || 'ChatGPT Clone'}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            className="p-2 rounded-lg hover:bg-accent transition-colors"
            title="Help"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => window.open('https://github.com/your-username/chatgpt-clone', '_blank')}
            className="p-2 rounded-lg hover:bg-accent transition-colors"
            title="View on GitHub"
          >
            <Github className="w-4 h-4" />
          </button>
          
          <button
            className="p-2 rounded-lg hover:bg-accent transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  )
}