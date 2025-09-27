'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/EnhancedSidebar';
import { Conversation, Message } from '@/types';
import { conversationService } from '@/services/api';

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await conversationService.getConversations();
      setConversations(data);
      if (data.length > 0 && !currentConversation) {
        setCurrentConversation(data[0]);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversation(null);
  };

  const handleConversationSelect = (conversation: Conversation) => {
    setCurrentConversation(conversation);
  };

  const handleConversationCreated = (conversation: Conversation) => {
    setConversations(prev => [conversation, ...prev]);
    setCurrentConversation(conversation);
  };

  const handleConversationDeleted = (conversationId: number) => {
    setConversations(prev => prev.filter(c => c.id !== conversationId));
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <Sidebar
        conversations={conversations}
        currentConversation={currentConversation}
        onConversationSelect={handleConversationSelect}
        onNewConversation={handleNewConversation}
        onConversationDeleted={handleConversationDeleted}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-80' : 'ml-0'}`}>
        <ChatInterface
          conversation={currentConversation}
          onConversationCreated={handleConversationCreated}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
      </div>
    </div>
  );
}