'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Send, Square, Mic, MicOff } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
  onStop: () => void
}

export default function ChatInput({ onSendMessage, isLoading, onStop }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [isListening, setIsListening] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim())
      setMessage('')
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser')
      return
    }

    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
    const recognition = new SpeechRecognition()

    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      setMessage(prev => prev + transcript)
      setIsListening(false)
    }

    recognition.onerror = () => {
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    if (isListening) {
      recognition.stop()
    } else {
      recognition.start()
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
    }
  }, [message])

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-end gap-2 p-3 bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          {/* Text Input */}
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e: any) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isLoading ? "AI is thinking..." : "Type your message... (Shift+Enter for new line)"}
            disabled={isLoading}
            className={cn(
              "flex-1 min-h-[20px] max-h-[120px] resize-none border-0 bg-transparent p-0 text-sm",
              "focus:ring-0 focus:outline-none",
              "placeholder:text-gray-500 dark:placeholder:text-gray-400",
              isLoading && "opacity-50"
            )}
            rows={1}
          />

          {/* Action Buttons */}
          <div className="flex items-center gap-1 flex-shrink-0">
            {/* Voice Input Button */}
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleVoiceInput}
              disabled={isLoading}
              className={cn(
                "w-8 h-8 p-0 rounded-full",
                isListening && "bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400"
              )}
            >
              {isListening ? (
                <MicOff className="w-4 h-4" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </Button>

            {/* Send/Stop Button */}
            {isLoading ? (
              <Button
                type="button"
                onClick={onStop}
                size="sm"
                variant="destructive"
                className="w-8 h-8 p-0 rounded-full"
              >
                <Square className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                type="submit"
                disabled={!message.trim()}
                size="sm"
                className={cn(
                  "w-8 h-8 p-0 rounded-full",
                  "bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-700",
                  "transition-colors"
                )}
              >
                <Send className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Help Text */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
          {isListening ? (
            <span className="text-red-500 animate-pulse">🎤 Listening...</span>
          ) : (
            <span>
              I can search the internet for real-time information and use AI tools to help you
            </span>
          )}
        </div>
      </form>
    </div>
  )
}

// Add speech recognition types
declare global {
  interface Window {
    webkitSpeechRecognition: any
    SpeechRecognition: any
  }
}