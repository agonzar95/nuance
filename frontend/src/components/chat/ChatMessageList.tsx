'use client'

/**
 * CAP-001: Chat Message List
 *
 * Displays a scrollable list of chat messages between user and AI.
 * - User messages on right, AI on left
 * - Support for streaming messages that update in real-time
 * - Auto-scroll to newest message
 * - Typing indicator during AI response
 */

import { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'

// ============================================================================
// Types
// ============================================================================

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: Date
  isStreaming?: boolean
}

export interface ChatMessageListProps {
  /** Array of messages to display */
  messages: ChatMessage[]
  /** Streaming content for in-progress AI response */
  streamingContent?: string
  /** Whether AI is currently generating a response */
  isLoading?: boolean
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function ChatMessageList({
  messages,
  streamingContent,
  isLoading,
  className,
}: ChatMessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on new messages or streaming content
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  return (
    <div className={cn('flex-1 overflow-y-auto p-4 space-y-4', className)}>
      {messages.length === 0 && !streamingContent && !isLoading && (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <p>Start a conversation...</p>
        </div>
      )}

      {messages.map((message) => (
        <ChatBubble key={message.id} message={message} />
      ))}

      {/* Streaming message (AI response in progress) */}
      {streamingContent && (
        <ChatBubble
          message={{
            id: 'streaming',
            role: 'assistant',
            content: streamingContent,
            createdAt: new Date(),
            isStreaming: true,
          }}
        />
      )}

      {/* Typing indicator (waiting for AI to start responding) */}
      {isLoading && !streamingContent && <TypingIndicator />}

      {/* Scroll anchor */}
      <div ref={scrollRef} />
    </div>
  )
}

// ============================================================================
// ChatBubble Component
// ============================================================================

interface ChatBubbleProps {
  message: ChatMessage
}

function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-2',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground',
          message.isStreaming && 'animate-pulse'
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {message.isStreaming && (
          <span
            className="inline-block w-2 h-4 bg-current animate-blink ml-1"
            aria-hidden="true"
          />
        )}
      </div>
    </div>
  )
}

// ============================================================================
// TypingIndicator Component
// ============================================================================

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-muted rounded-lg px-4 py-3">
        <div className="flex items-center gap-1">
          <span
            className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <span
            className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <span
            className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Styles - Add to your global CSS or Tailwind config
// ============================================================================

/*
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.animate-blink {
  animation: blink 1s step-end infinite;
}
*/
