"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Send, User, Bot, AlertCircle, Loader2, Search } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Message {
  id?: number;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

interface StreamEvent {
  type: "chunk" | "start_streaming" | "complete" | "error" | "conversation_created" | "rag_searching" | "rag_found" | "rag_failed";
  content?: string;
  message?: string;
  conversation_id?: number;
  message_id?: number;
  code?: number;
  timestamp?: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [streamingMessage, setStreamingMessage] = useState("");
  const [ragStatus, setRagStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { token } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const handleStreamResponse = async (response: Response) => {
    const reader = response.body?.getReader();
    if (!reader) throw new Error("No reader available");

    const decoder = new TextDecoder();
    let buffer = "";
    let currentStreamingContent = "";
    
    setStreamingMessage("");

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data: StreamEvent = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case "conversation_created":
                  if (data.conversation_id) {
                    setConversationId(data.conversation_id);
                  }
                  break;
                
                case "rag_searching":
                  setRagStatus("🔍 Searching for current information...");
                  break;
                
                case "rag_found":
                  setRagStatus("✅ Found relevant information");
                  setTimeout(() => setRagStatus(null), 2000);
                  break;
                
                case "rag_failed":
                  setRagStatus("⚠️ Continuing without search...");
                  setTimeout(() => setRagStatus(null), 2000);
                  break;
                
                case "start_streaming":
                  currentStreamingContent = "";
                  setStreamingMessage("");
                  break;
                
                case "chunk":
                  if (data.content) {
                    currentStreamingContent += data.content;
                    setStreamingMessage(currentStreamingContent);
                  }
                  break;
                
                case "complete":
                  if (data.message_id) {
                    const finalMessage: Message = {
                      id: data.message_id,
                      role: "assistant",
                      content: currentStreamingContent,
                      timestamp: new Date().toISOString(),
                    };
                    setMessages(prev => [...prev, finalMessage]);
                    setStreamingMessage("");
                    setRagStatus(null);
                  }
                  break;
                
                case "error":
                  setError(data.message || "An error occurred");
                  setStreamingMessage("");
                  setRagStatus(null);
                  break;
              }
            } catch (e) {
              console.warn("Failed to parse SSE data:", line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setError(null);
    setRagStatus(null);

    // Create abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("/api/v1/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_id: conversationId,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || `HTTP ${response.status}`);
      }

      await handleStreamResponse(response);
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Request aborted");
      } else {
        console.error("Chat error:", error);
        setError(error.message || "Failed to send message");
      }
    } finally {
      setIsLoading(false);
      setStreamingMessage("");
      setRagStatus(null);
    }
  };

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      setStreamingMessage("");
      setRagStatus(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const MessageContent = ({ content }: { content: string }) => (
    <ReactMarkdown
      className="prose prose-sm max-w-none dark:prose-invert prose-pre:bg-gray-800 prose-pre:text-gray-100"
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\\w+)/.exec(className || "");
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark}
              language={match[1]}
              PreTag="div"
              className="rounded-md"
              {...props}
            >
              {String(children).replace(/\\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code
              className="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm"
              {...props}
            >
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                GPT.R1 Assistant
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Professional AI Chat with Real-time Streaming
              </p>
            </div>
          </div>
          
          {conversationId && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Conversation #{conversationId}
            </div>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        {messages.length === 0 && !streamingMessage && (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-2">
              Welcome to GPT.R1
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              Start a conversation with our advanced AI assistant. Ask questions, get help with coding, or discuss any topic.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className="flex items-start space-x-4">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === "user"
                  ? "bg-blue-500"
                  : "bg-gradient-to-r from-purple-500 to-pink-500"
              }`}
            >
              {message.role === "user" ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-white" />
              )}
            </div>
            <Card className="flex-1 border-0 shadow-sm bg-white dark:bg-gray-800">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {message.role === "user" ? "You" : "Assistant"}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <MessageContent content={message.content} />
              </CardContent>
            </Card>
          </div>
        ))}

        {/* Streaming Message */}
        {streamingMessage && (
          <div className="flex items-start space-x-4">
            <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-gradient-to-r from-purple-500 to-pink-500">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <Card className="flex-1 border-0 shadow-sm bg-white dark:bg-gray-800">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Assistant
                  </span>
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-3 h-3 animate-spin text-purple-500" />
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Typing...
                    </span>
                  </div>
                </div>
                <MessageContent content={streamingMessage} />
                <div className="w-2 h-4 bg-purple-500 animate-pulse inline-block ml-1" />
              </CardContent>
            </Card>
          </div>
        )}

        {/* RAG Status */}
        {ragStatus && (
          <div className="flex items-center justify-center">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg px-4 py-2">
              <div className="flex items-center space-x-2 text-blue-700 dark:text-blue-300">
                <Search className="w-4 h-4" />
                <span className="text-sm">{ragStatus}</span>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="flex items-center justify-center">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-2">
              <div className="flex items-center space-x-2 text-red-700 dark:text-red-300">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex space-x-4">
          <div className="flex-1">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
              disabled={isLoading}
              className="min-h-[48px] resize-none bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          
          {isLoading ? (
            <Button
              onClick={stopGeneration}
              variant="outline"
              size="icon"
              className="h-12 w-12 border-red-300 text-red-600 hover:bg-red-50"
            >
              <AlertCircle className="w-5 h-5" />
            </Button>
          ) : (
            <Button
              onClick={sendMessage}
              disabled={!inputMessage.trim()}
              size="icon"
              className="h-12 w-12 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              <Send className="w-5 h-5" />
            </Button>
          )}
        </div>
        
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
          GPT.R1 with Real-time Streaming • Enhanced with RAG Search • Professional AI Assistant
        </div>
      </div>
    </div>
  );
}