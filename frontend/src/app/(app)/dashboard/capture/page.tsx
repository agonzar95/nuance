'use client'

/**
 * CAP-009: Capture Page Container
 *
 * Page-level container that orchestrates all capture components:
 * - ChatMessageList (CAP-001) - Display conversation
 * - ChatInput (CAP-002) - Text input
 * - VoiceInput (CAP-003) - Voice input
 * - GhostCard (CAP-004) - Loading state during extraction
 * - ConfidenceValidation (CAP-005) - Low confidence review
 * - ActionEditForm (CAP-006) - Edit extracted actions
 *
 * Flow:
 * 1. User sends text/voice input
 * 2. Show ghost card while extracting
 * 3. If confidence >= 0.7, auto-save action
 * 4. If confidence < 0.7, show validation UI
 * 5. On confirm/edit, save to database
 */

import { useReducer, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { ChatMessageList, type ChatMessage } from '@/components/chat/ChatMessageList'
import { ChatInput } from '@/components/chat/ChatInput'
import { GhostCard } from '@/components/capture/GhostCard'
import { ConfidenceValidation, type ExtractionForValidation } from '@/components/capture/ConfidenceValidation'
import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'
import type { EnrichedAction } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

interface PendingExtraction {
  messageId: string
  rawText: string
  status: 'extracting' | 'validating' | 'saving'
  action?: EnrichedAction
}

interface CaptureState {
  messages: ChatMessage[]
  pendingExtraction: PendingExtraction | null
  validationQueue: EnrichedAction[]
  error: string | null
}

type CaptureAction =
  | { type: 'ADD_USER_MESSAGE'; message: ChatMessage }
  | { type: 'ADD_ASSISTANT_MESSAGE'; message: ChatMessage }
  | { type: 'START_EXTRACTION'; messageId: string; rawText: string }
  | { type: 'EXTRACTION_COMPLETE'; actions: EnrichedAction[] }
  | { type: 'AUTO_CONFIRM'; action: EnrichedAction }
  | { type: 'NEEDS_VALIDATION'; action: EnrichedAction }
  | { type: 'VALIDATION_CONFIRMED' }
  | { type: 'SET_ERROR'; error: string }
  | { type: 'CLEAR_ERROR' }

// ============================================================================
// Reducer
// ============================================================================

const initialState: CaptureState = {
  messages: [],
  pendingExtraction: null,
  validationQueue: [],
  error: null,
}

function captureReducer(state: CaptureState, action: CaptureAction): CaptureState {
  switch (action.type) {
    case 'ADD_USER_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.message],
      }

    case 'ADD_ASSISTANT_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.message],
      }

    case 'START_EXTRACTION':
      return {
        ...state,
        pendingExtraction: { messageId: action.messageId, rawText: action.rawText, status: 'extracting' },
        error: null,
      }

    case 'EXTRACTION_COMPLETE':
      return {
        ...state,
        pendingExtraction: null,
        validationQueue: action.actions.filter(a => a.confidence.confidence < 0.7),
      }

    case 'AUTO_CONFIRM':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            id: `confirm-${Date.now()}`,
            role: 'assistant',
            content: `Got it! I've added "${action.action.title}" to your inbox.`,
            createdAt: new Date(),
          },
        ],
      }

    case 'NEEDS_VALIDATION':
      return {
        ...state,
        validationQueue: [...state.validationQueue, action.action],
        pendingExtraction: { ...state.pendingExtraction!, status: 'validating' },
      }

    case 'VALIDATION_CONFIRMED':
      return {
        ...state,
        validationQueue: state.validationQueue.slice(1),
        pendingExtraction: null,
      }

    case 'SET_ERROR':
      return {
        ...state,
        error: action.error,
        pendingExtraction: null,
      }

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }

    default:
      return state
  }
}

// ============================================================================
// Component
// ============================================================================

export default function CapturePage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [state, dispatch] = useReducer(captureReducer, initialState)

  // Mutation for processing text through the AI
  const processMutation = useMutation({
    mutationFn: async (text: string) => {
      return api.ai.process({ text })
    },
    onSuccess: async (result) => {
      if (result.intent === 'capture' && result.capture) {
        const actions = result.capture.actions

        for (const enrichedAction of actions) {
          if (enrichedAction.confidence.confidence >= 0.7) {
            // Auto-save high confidence actions
            await api.actions.create({
              title: enrichedAction.title,
              raw_input: enrichedAction.raw_segment,
              estimated_minutes: enrichedAction.estimated_minutes,
              avoidance_weight: enrichedAction.avoidance.weight,
              complexity: enrichedAction.complexity.complexity,
              status: 'inbox',
            })
            dispatch({ type: 'AUTO_CONFIRM', action: enrichedAction })
          } else {
            // Queue for validation
            dispatch({ type: 'NEEDS_VALIDATION', action: enrichedAction })
          }
        }

        // Invalidate actions cache
        queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
        dispatch({ type: 'EXTRACTION_COMPLETE', actions })
      } else if (result.intent === 'coaching' && result.coaching) {
        // Handle coaching response
        dispatch({
          type: 'ADD_ASSISTANT_MESSAGE',
          message: {
            id: `coaching-${Date.now()}`,
            role: 'assistant',
            content: result.coaching.message,
            createdAt: new Date(),
          },
        })
      }
    },
    onError: (error) => {
      dispatch({ type: 'SET_ERROR', error: error.message })
    },
  })

  // Mutation for saving validated actions
  const saveActionMutation = useMutation({
    mutationFn: async (action: EnrichedAction) => {
      return api.actions.create({
        title: action.title,
        raw_input: action.raw_segment,
        estimated_minutes: action.estimated_minutes,
        avoidance_weight: action.avoidance.weight,
        complexity: action.complexity.complexity,
        status: 'inbox',
      })
    },
    onSuccess: (savedAction) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
      dispatch({ type: 'VALIDATION_CONFIRMED' })
      dispatch({
        type: 'ADD_ASSISTANT_MESSAGE',
        message: {
          id: `saved-${Date.now()}`,
          role: 'assistant',
          content: `Added "${savedAction.title}" to your inbox.`,
          createdAt: new Date(),
        },
      })
    },
    onError: (error) => {
      dispatch({ type: 'SET_ERROR', error: error.message })
    },
  })

  const handleSend = useCallback((text: string) => {
    const messageId = `msg-${Date.now()}`

    // Add user message
    dispatch({
      type: 'ADD_USER_MESSAGE',
      message: {
        id: messageId,
        role: 'user',
        content: text,
        createdAt: new Date(),
      },
    })

    // Start extraction
    dispatch({ type: 'START_EXTRACTION', messageId, rawText: text })
    processMutation.mutate(text)
  }, [processMutation])

  const handleValidationConfirm = useCallback((actions: EnrichedAction[]) => {
    for (const action of actions) {
      saveActionMutation.mutate(action)
    }
  }, [saveActionMutation])

  const handleValidationEdit = useCallback((action: EnrichedAction, _index: number) => {
    // For now, just confirm the action as-is
    // A more complete implementation would show an edit form
    saveActionMutation.mutate(action)
  }, [saveActionMutation])

  const handleValidationDismiss = useCallback(() => {
    dispatch({ type: 'VALIDATION_CONFIRMED' })
  }, [])

  const currentValidation = state.validationQueue[0]
  const isLoading = processMutation.isPending || saveActionMutation.isPending

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b bg-white">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="text-gray-500 hover:text-gray-700"
            aria-label="Back to dashboard"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <h1 className="text-lg font-semibold text-gray-900">Capture</h1>
        </div>
        <span className="text-sm text-gray-500">
          {state.messages.length} messages
        </span>
      </header>

      {/* Error Banner */}
      {state.error && (
        <div className="px-4 py-3 bg-red-50 border-b border-red-200">
          <div className="flex items-center justify-between">
            <p className="text-sm text-red-700">{state.error}</p>
            <button
              onClick={() => dispatch({ type: 'CLEAR_ERROR' })}
              className="text-red-500 hover:text-red-700"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <ChatMessageList
        messages={state.messages}
        isLoading={state.pendingExtraction?.status === 'extracting'}
        className="flex-1"
      />

      {/* Ghost Card (during extraction) */}
      {state.pendingExtraction?.status === 'extracting' && (
        <div className="px-4 py-2">
          <GhostCard
            rawText={state.pendingExtraction.rawText}
            status="extracting"
          />
        </div>
      )}

      {/* Validation UI */}
      {currentValidation && (
        <div className="border-t bg-gray-50 p-4">
          <ConfidenceValidation
            extraction={{
              actions: [currentValidation],
              confidence: currentValidation.confidence.confidence,
              ambiguities: currentValidation.confidence.ambiguities,
            }}
            onConfirm={handleValidationConfirm}
            onEdit={handleValidationEdit}
            onDismiss={handleValidationDismiss}
          />
        </div>
      )}

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        disabled={isLoading || !!currentValidation}
        placeholder="What's on your mind? Dump your thoughts here..."
        showVoiceInput={true}
      />
    </div>
  )
}
