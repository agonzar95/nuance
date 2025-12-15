'use client'

/**
 * EXE-009: Coaching Overlay
 *
 * Full-screen overlay providing supportive conversation when user is stuck.
 * Uses multi-turn AI chat to help users work through blocks without judgment.
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { X, Send } from 'lucide-react'
import { ChatMessageList, type ChatMessage } from '@/components/chat/ChatMessageList'
import { useProcessStream } from '@/hooks/useSSE'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export type StuckReason = 'too_big' | 'dont_know' | 'dont_want' | 'other'

export type CoachingResolution =
  | { type: 'continue'; insight?: string }
  | { type: 'breakdown'; steps: string[] }
  | { type: 'defer'; reason: string }
  | { type: 'drop'; reason: string }

export interface CoachingOverlayProps {
  action: Action
  stuckReason: StuckReason
  open: boolean
  onClose: () => void
  onResolution?: (resolution: CoachingResolution) => void
}

// ============================================================================
// Helper Functions
// ============================================================================

function getInitialPrompt(stuckReason: StuckReason, taskTitle: string): string {
  const prompts: Record<StuckReason, string> = {
    too_big: `I'm trying to work on "${taskTitle}" but it feels overwhelming. I don't know where to start.`,
    dont_know: `I need to do "${taskTitle}" but I'm not sure how to approach it. Can you help me figure out what to do?`,
    dont_want: `I've been putting off "${taskTitle}" and I'm not sure why. I know I should do it but I just can't seem to start.`,
    other: `I'm stuck on "${taskTitle}" and could use some help working through it.`,
  }
  return prompts[stuckReason]
}

// ============================================================================
// Component
// ============================================================================

export function CoachingOverlay({
  action,
  stuckReason,
  open,
  onClose,
  onResolution
}: CoachingOverlayProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [hasInitiated, setHasInitiated] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const streamingContentRef = useRef('')

  const { content: streamingContent, isStreaming, process, reset: resetStream } = useProcessStream({
    onMessage: (chunk) => {
      streamingContentRef.current += chunk
    },
    onComplete: () => {
      // Add the completed AI message
      if (streamingContentRef.current) {
        setMessages(prev => [...prev, {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: streamingContentRef.current,
          createdAt: new Date(),
        }])
        streamingContentRef.current = ''
      }
    },
    onError: (error) => {
      console.error('Coaching error:', error)
      // Add a fallback message
      setMessages(prev => [...prev, {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: "I hear you - this sounds challenging. What's one tiny thing you could do in the next 2 minutes to make progress?",
        createdAt: new Date(),
      }])
    },
  })

  // Initialize conversation when overlay opens
  useEffect(() => {
    if (open && !hasInitiated) {
      const initialUserMessage = getInitialPrompt(stuckReason, action.title)

      // Add user's initial message
      setMessages([{
        id: 'user-initial',
        role: 'user',
        content: initialUserMessage,
        createdAt: new Date(),
      }])

      // Send to coaching AI
      process({
        text: initialUserMessage,
        taskId: action.id,
        taskTitle: action.title,
        forceIntent: 'coaching',
      })

      setHasInitiated(true)
    }
  }, [open, hasInitiated, stuckReason, action, process])

  // Reset when closing
  useEffect(() => {
    if (!open) {
      setMessages([])
      setInput('')
      setHasInitiated(false)
      streamingContentRef.current = ''
      resetStream()
    }
  }, [open, resetStream])

  // Focus input when not streaming
  useEffect(() => {
    if (!isStreaming && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isStreaming])

  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return

    const userMessage = input.trim()
    setInput('')
    streamingContentRef.current = ''

    // Add user message to list
    setMessages(prev => [...prev, {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      createdAt: new Date(),
    }])

    // Send to coaching AI
    await process({
      text: userMessage,
      taskId: action.id,
      taskTitle: action.title,
      forceIntent: 'coaching',
    })
  }, [input, isStreaming, action.id, action.title, process])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
    if (e.key === 'Escape') {
      onClose()
    }
  }

  const handleResolution = (type: CoachingResolution['type']) => {
    // For now, just close with a basic resolution
    // In future, could parse AI responses for suggested actions
    onResolution?.({ type } as CoachingResolution)
    onClose()
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h2 className="font-medium">Let's work through this</h2>
          <p className="text-sm text-muted-foreground">
            {action.title}
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
          aria-label="Close coaching"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <ChatMessageList
        messages={messages}
        streamingContent={streamingContentRef.current || (isStreaming ? '' : undefined)}
        isLoading={isStreaming && !streamingContentRef.current}
        className="flex-1"
      />

      {/* Quick Resolution Buttons */}
      <div className="px-4 py-2 border-t bg-muted/30">
        <div className="flex flex-wrap gap-2 text-xs">
          <button
            onClick={() => handleResolution('continue')}
            className="px-3 py-1.5 rounded-full border hover:bg-muted transition-colors"
          >
            I'm ready to try again
          </button>
          <button
            onClick={() => handleResolution('defer')}
            className="px-3 py-1.5 rounded-full border hover:bg-muted transition-colors"
          >
            Save for later
          </button>
          <button
            onClick={() => handleResolution('drop')}
            className="px-3 py-1.5 rounded-full border hover:bg-muted transition-colors text-muted-foreground"
          >
            Drop this task
          </button>
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex gap-2"
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your thoughts..."
            className="flex-1 px-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg disabled:opacity-50 transition-opacity"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  )
}
