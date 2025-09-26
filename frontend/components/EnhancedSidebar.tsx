'use client';

import { useState, useEffect } from 'react';
import { Plus, MessageSquare, Trash2, Edit3, Search, Settings, User, Moon, Sun, Zap, History, Star, Archive, Filter, Check, X } from 'lucide-react';
import { Conversation } from '@/types';
import { conversationService } from '@/services/api';

interface EnhancedSidebarProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  onConversationSelect: (conversation: Conversation) => void;
  onNewConversation: () => void;
  onConversationDeleted: (conversationId: number) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export default function EnhancedSidebar({
  conversations,
  currentConversation,
  onConversationSelect,
  onNewConversation,
  onConversationDeleted,
  isOpen,
  onToggle,
}: EnhancedSidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [darkMode, setDarkMode] = useState(true);
  const [filter, setFilter] = useState<'all' | 'recent' | 'starred' | 'archived'>('all');

  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || 
      (filter === 'recent' && new Date(conv.updated_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000));
    return matchesSearch && matchesFilter;
  });

  const handleDeleteConversation = async (conversationId: number) => {
    try {
      await conversationService.deleteConversation(conversationId);
      onConversationDeleted(conversationId);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const startEditing = (conversation: Conversation) => {
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditTitle('');
  };

  const saveEdit = async () => {
    if (!editingId || !editTitle.trim()) return;

    try {
      await conversationService.updateConversation(editingId, { title: editTitle.trim() });
      setEditingId(null);
      setEditTitle('');
      // Note: You might want to refresh the conversations list here
    } catch (error) {
      console.error('Failed to update conversation:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const getConversationPreview = (conversation: Conversation) => {
    const lastMessage = conversation.messages?.[conversation.messages.length - 1];
    if (!lastMessage) return 'New conversation';
    return lastMessage.content.substring(0, 60) + (lastMessage.content.length > 60 ? '...' : '');
  };

  return (
    <div className={`glass border-r border-gray-700/50 flex flex-col h-screen transition-all duration-300 ${
      isOpen ? 'w-80' : 'w-0'
    } overflow-hidden relative z-20`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="space-y-4">
          {/* New Chat Button */}
          <button
            onClick={onNewConversation}
            className="enhanced-button w-full bg-green-500/20 hover:bg-green-500/30 border border-green-400/30 text-green-400 rounded-2xl p-4 flex items-center space-x-3 transition-all duration-300 hover:scale-105 shadow-glow"
          >
            <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
              <Plus className="h-4 w-4" />
            </div>
            <span className="font-semibold">New Conversation</span>
          </button>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-800/50 border border-gray-600/50 rounded-xl pl-10 pr-4 py-3 text-white placeholder-gray-400 enhanced-focus smooth-transition"
            />
          </div>

          {/* Filter Buttons */}
          <div className="flex space-x-2">
            {[
              { key: 'all', label: 'All', icon: MessageSquare },
              { key: 'recent', label: 'Recent', icon: History },
              { key: 'starred', label: 'Starred', icon: Star },
              { key: 'archived', label: 'Archive', icon: Archive },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setFilter(key as any)}
                className={`enhanced-button px-3 py-2 rounded-lg text-xs transition-all duration-300 ${
                  filter === key
                    ? 'bg-blue-500/20 border-blue-400/30 text-blue-400'
                    : 'bg-gray-700/50 border-gray-600/50 text-gray-300 hover:bg-gray-600/50'
                }`}
                title={label}
              >
                <Icon className="h-3 w-3" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
        {filteredConversations.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">
              {searchTerm ? 'No conversations found' : 'No conversations yet'}
            </p>
            <p className="text-xs mt-2">
              {searchTerm ? 'Try a different search term' : 'Start a new conversation to get started'}
            </p>
          </div>
        ) : (
          filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`modern-card rounded-xl p-4 transition-all duration-300 cursor-pointer hover:scale-105 group ${
                currentConversation?.id === conversation.id
                  ? 'bg-blue-500/20 border-blue-400/30 shadow-glow'
                  : 'bg-gray-800/30 border-gray-600/30 hover:bg-gray-700/50'
              }`}
              onClick={() => onConversationSelect(conversation)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {editingId === conversation.id ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') saveEdit();
                          if (e.key === 'Escape') cancelEditing();
                        }}
                        className="flex-1 bg-gray-700 text-white text-sm font-medium rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        autoFocus
                      />
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          saveEdit();
                        }}
                        className="p-1 hover:bg-green-600/50 rounded text-green-400 transition-colors"
                      >
                        <Check className="h-3 w-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          cancelEditing();
                        }}
                        className="p-1 hover:bg-red-600/50 rounded text-red-400 transition-colors"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ) : (
                    <h3 className={`text-sm font-medium truncate ${
                      currentConversation?.id === conversation.id ? 'text-blue-400' : 'text-white'
                    }`}>
                      {conversation.title}
                    </h3>
                  )}
                  
                  <p className="text-xs text-gray-400 mt-1 truncate">
                    {getConversationPreview(conversation)}
                  </p>
                  
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-gray-500">
                      {formatDate(conversation.updated_at)}
                    </span>
                    
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          startEditing(conversation);
                        }}
                        className="p-1 hover:bg-gray-600/50 rounded text-gray-400 hover:text-white transition-colors"
                        title="Rename conversation"
                      >
                        <Edit3 className="h-3 w-3" />
                      </button>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm('Are you sure you want to delete this conversation?')) {
                            handleDeleteConversation(conversation.id);
                          }
                        }}
                        className="p-1 hover:bg-red-600/50 rounded text-gray-400 hover:text-red-400 transition-colors"
                        title="Delete conversation"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Star functionality could be implemented
                        }}
                        className="p-1 hover:bg-yellow-600/50 rounded text-gray-400 hover:text-yellow-400 transition-colors"
                        title="Star conversation"
                      >
                        <Star className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-700/50 p-4 space-y-2">
        <div className="text-xs text-gray-500 text-center">
          {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
        </div>
        
        <div className="flex items-center justify-between">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="enhanced-button p-2 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl transition-all duration-300 hover:scale-105"
            title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
          >
            {darkMode ? <Sun className="h-4 w-4 text-yellow-400" /> : <Moon className="h-4 w-4 text-blue-400" />}
          </button>

          <button
            className="enhanced-button p-2 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl transition-all duration-300 hover:scale-105"
            title="Settings"
          >
            <Settings className="h-4 w-4 text-gray-400" />
          </button>

          <button
            className="enhanced-button p-2 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-xl transition-all duration-300 hover:scale-105"
            title="User profile"
          >
            <User className="h-4 w-4 text-gray-400" />
          </button>

          <button
            className="enhanced-button p-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400/30 rounded-xl transition-all duration-300 hover:scale-105"
            title="Advanced features"
          >
            <Zap className="h-4 w-4 text-purple-400" />
          </button>
        </div>

        <div className="text-center text-xs text-gray-600">
          Enhanced ChatGPT Clone v2.0
        </div>
      </div>
    </div>
  );
}