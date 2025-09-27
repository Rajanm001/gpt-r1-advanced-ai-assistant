'use client';

// 🚀 Production ChatGPT Clone - Main Application
// ✨ Clean, Modern, Error-Free Implementation

import React from 'react';
import ProductionChatInterface from '@/components/ProductionChatInterface';

export default function ProductionChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                ChatGPT Clone Production
              </h1>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-sm font-medium rounded-full">
                ✅ Online
              </div>
              <div className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm font-medium rounded-full">
                v2.0 Production
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Interface */}
      <main className="h-[calc(100vh-4rem)]">
        <ProductionChatInterface />
      </main>
    </div>
  );
}