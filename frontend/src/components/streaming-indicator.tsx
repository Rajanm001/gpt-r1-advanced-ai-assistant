'use client'

import { Search, Brain, Loader2, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface RAGStatus {
  analyzing: boolean
  searchUsed: boolean
  enhanced: boolean
}

interface StreamingIndicatorProps {
  step: string
  ragStatus: RAGStatus
  isTyping: boolean
}

export default function StreamingIndicator({ step, ragStatus, isTyping }: StreamingIndicatorProps) {
  return (
    <div className="flex items-start gap-3 max-w-4xl mr-auto">
      {/* AI Avatar */}
      <div className="w-8 h-8 flex-shrink-0 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
        <Brain className="w-4 h-4 text-white" />
      </div>

      {/* Status Container */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 shadow-sm">
        <div className="space-y-3">
          {/* Current Step */}
          <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>{step}</span>
          </div>

          {/* RAG Status */}
          <div className="flex items-center gap-4 text-xs">
            {/* Search Analysis */}
            <div className={cn(
              "flex items-center gap-1 transition-colors",
              ragStatus.analyzing ? "text-blue-500" : 
              ragStatus.enhanced ? "text-green-500" : "text-gray-400"
            )}>
              {ragStatus.analyzing ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : ragStatus.enhanced ? (
                <CheckCircle className="w-3 h-3" />
              ) : (
                <Search className="w-3 h-3" />
              )}
              <span>
                {ragStatus.analyzing ? "Analyzing..." : 
                 ragStatus.enhanced ? "Search enhanced" : "Knowledge base"}
              </span>
            </div>

            {/* Processing Status */}
            <div className={cn(
              "flex items-center gap-1 transition-colors",
              isTyping ? "text-green-500" : "text-gray-400"
            )}>
              {isTyping ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Brain className="w-3 h-3" />
              )}
              <span>
                {isTyping ? "Generating..." : "Processing"}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
            <div 
              className="bg-gradient-to-r from-purple-500 to-blue-600 h-1 rounded-full transition-all duration-300 animate-pulse"
              style={{ 
                width: ragStatus.analyzing ? '33%' : 
                       ragStatus.enhanced ? '66%' : 
                       isTyping ? '90%' : '10%' 
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}