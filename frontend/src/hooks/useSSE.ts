'use client'

/**
 * FE-003: SSE Handler Hook
 *
 * Hook for connecting to Server-Sent Events endpoints.
 * Provides streaming message content with connection lifecycle management.
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

// ============================================================================
// Types
// ============================================================================

interface SSEOptions {
  /** The SSE endpoint URL */
  url: string
  /** Callback for each message chunk */
  onMessage?: (content: string) => void
  /** Callback when stream completes */
  onComplete?: () => void
  /** Callback on error */
  onError?: (error: Error) => void
  /** Callback for non-streaming results (capture/command intents) */
  onResult?: (result: unknown) => void
}

interface SSEState {
  /** Accumulated content from stream */
  content: string
  /** Whether stream is currently active */
  isStreaming: boolean
  /** Error if stream failed */
  error: Error | null
}

interface SSEReturn extends SSEState {
  /** Start the SSE connection */
  start: () => Promise<void>
  /** Stop the SSE connection */
  stop: () => void
  /** Reset state to initial values */
  reset: () => void
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for handling Server-Sent Events from the AI streaming endpoints.
 *
 * @example
 * ```tsx
 * const { content, isStreaming, start, stop } = useSSE({
 *   url: `${API_URL}/api/ai/process/stream`,
 *   onComplete: () => console.log('Stream complete'),
 *   onError: (err) => toast.error(err.message)
 * })
 *
 * // Start streaming
 * await start()
 * ```
 */
export function useSSE(options: SSEOptions): SSEReturn {
  const [state, setState] = useState<SSEState>({
    content: '',
    isStreaming: false,
    error: null,
  })

  const eventSourceRef = useRef<EventSource | null>(null)
  const optionsRef = useRef(options)
  optionsRef.current = options

  const stop = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setState((s) => ({ ...s, isStreaming: false }))
  }, [])

  const reset = useCallback(() => {
    stop()
    setState({ content: '', isStreaming: false, error: null })
  }, [stop])

  const start = useCallback(async () => {
    // Clean up any existing connection
    stop()

    // Get auth token
    const supabase = createClient()
    const {
      data: { session },
    } = await supabase.auth.getSession()
    const token = session?.access_token

    if (!token) {
      const error = new Error('Not authenticated')
      setState((s) => ({ ...s, error }))
      optionsRef.current.onError?.(error)
      return
    }

    // Build URL with token as query param (EventSource doesn't support headers)
    const url = new URL(optionsRef.current.url)
    url.searchParams.set('token', token)

    // Create EventSource
    const eventSource = new EventSource(url.toString())
    eventSourceRef.current = eventSource

    setState({ content: '', isStreaming: true, error: null })

    // Handle message events (streaming content)
    eventSource.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.content) {
          setState((s) => {
            const newContent = s.content + data.content
            optionsRef.current.onMessage?.(data.content)
            return { ...s, content: newContent }
          })
        }
      } catch {
        // Ignore parse errors
      }
    })

    // Handle result events (non-streaming intents)
    eventSource.addEventListener('result', (event) => {
      try {
        const data = JSON.parse(event.data)
        optionsRef.current.onResult?.(data)
      } catch {
        // Ignore parse errors
      }
    })

    // Handle completion
    eventSource.addEventListener('done', () => {
      eventSource.close()
      eventSourceRef.current = null
      setState((s) => ({ ...s, isStreaming: false }))
      optionsRef.current.onComplete?.()
    })

    // Handle errors
    eventSource.addEventListener('error', (event) => {
      eventSource.close()
      eventSourceRef.current = null

      // Try to get error details from event
      let errorMessage = 'SSE connection failed'
      try {
        // @ts-expect-error - error event may have data
        if (event.data) {
          // @ts-expect-error - error event may have data
          const data = JSON.parse(event.data)
          errorMessage = data.error || errorMessage
        }
      } catch {
        // Use default message
      }

      const error = new Error(errorMessage)
      setState((s) => ({ ...s, isStreaming: false, error }))
      optionsRef.current.onError?.(error)
    })
  }, [stop])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      eventSourceRef.current?.close()
    }
  }, [])

  return {
    ...state,
    start,
    stop,
    reset,
  }
}

// ============================================================================
// Specialized Hooks
// ============================================================================

interface ProcessStreamOptions {
  /** Callback for streaming message chunks (coaching) */
  onMessage?: (content: string) => void
  /** Callback when stream completes */
  onComplete?: () => void
  /** Callback on error */
  onError?: (error: Error) => void
  /** Callback for non-streaming results (capture/command) */
  onResult?: (result: unknown) => void
}

/**
 * Hook for streaming AI process responses.
 * Handles both streaming (coaching) and non-streaming (capture/command) intents.
 *
 * @example
 * ```tsx
 * const { content, isStreaming, process } = useProcessStream({
 *   onComplete: () => console.log('Done'),
 *   onResult: (result) => {
 *     if (result.intent === 'capture') {
 *       // Handle captured actions
 *     }
 *   }
 * })
 *
 * // Process user input
 * await process({ text: "I need to buy groceries" })
 * ```
 */
export function useProcessStream(options: ProcessStreamOptions = {}) {
  const processApiUrl = globalThis.process?.env?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const [requestBody, setRequestBody] = useState<{
    text: string
    task_id?: string
    task_title?: string
    force_intent?: string
  } | null>(null)

  const sse = useSSE({
    url: `${processApiUrl}/api/ai/process/stream`,
    onMessage: options.onMessage,
    onComplete: options.onComplete,
    onError: options.onError,
    onResult: options.onResult,
  })

  const processMessage = useCallback(
    async (params: {
      text: string
      taskId?: string
      taskTitle?: string
      forceIntent?: 'capture' | 'coaching' | 'command'
    }) => {
      // For SSE, we need to send the body through query params or use fetch + SSE
      // Since EventSource doesn't support POST, we'll use fetch with streaming
      const supabase = createClient()
      const {
        data: { session },
      } = await supabase.auth.getSession()
      const token = session?.access_token

      if (!token) {
        options.onError?.(new Error('Not authenticated'))
        return
      }

      // Reset state
      sse.reset()

      // Build request body
      const body = {
        text: params.text,
        task_id: params.taskId,
        task_title: params.taskTitle,
        force_intent: params.forceIntent,
      }
      setRequestBody(body)

      // Use fetch with ReadableStream for POST requests
      try {
        const response = await fetch(`${processApiUrl}/api/ai/process/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
            Accept: 'text/event-stream',
          },
          body: JSON.stringify(body),
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        if (!response.body) {
          throw new Error('No response body')
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        // Process the stream
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // Process SSE events in buffer
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // Keep incomplete line

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              const eventType = line.slice(7)
              continue
            }
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  options.onMessage?.(parsed.content)
                } else if (parsed.intent) {
                  options.onResult?.(parsed)
                }
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }

        options.onComplete?.()
      } catch (error) {
        options.onError?.(error instanceof Error ? error : new Error(String(error)))
      }
    },
    [processApiUrl, sse, options]
  )

  return {
    content: sse.content,
    isStreaming: sse.isStreaming,
    error: sse.error,
    process: processMessage,
    stop: sse.stop,
    reset: sse.reset,
  }
}

/**
 * Hook for streaming chat responses.
 *
 * @example
 * ```tsx
 * const { content, isStreaming, sendMessage } = useChatStream({
 *   onComplete: () => setMessages(prev => [...prev, { role: 'assistant', content }])
 * })
 * ```
 */
export function useChatStream(options: {
  onMessage?: (content: string) => void
  onComplete?: (fullContent: string) => void
  onError?: (error: Error) => void
} = {}) {
  const chatApiUrl = globalThis.process?.env?.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const [content, setContent] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const contentRef = useRef('')

  const sendMessage = useCallback(
    async (messages: Array<{ role: 'user' | 'assistant'; content: string }>, system?: string) => {
      const supabase = createClient()
      const {
        data: { session },
      } = await supabase.auth.getSession()
      const token = session?.access_token

      if (!token) {
        const err = new Error('Not authenticated')
        setError(err)
        options.onError?.(err)
        return
      }

      // Reset state
      setContent('')
      contentRef.current = ''
      setIsStreaming(true)
      setError(null)

      try {
        const response = await fetch(`${chatApiUrl}/api/ai/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
            Accept: 'text/event-stream',
          },
          body: JSON.stringify({ messages, system }),
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        if (!response.body) {
          throw new Error('No response body')
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // Process lines
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  contentRef.current += parsed.content
                  setContent(contentRef.current)
                  options.onMessage?.(parsed.content)
                }
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }

        setIsStreaming(false)
        options.onComplete?.(contentRef.current)
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err))
        setError(error)
        setIsStreaming(false)
        options.onError?.(error)
      }
    },
    [chatApiUrl, options]
  )

  const reset = useCallback(() => {
    setContent('')
    contentRef.current = ''
    setIsStreaming(false)
    setError(null)
  }, [])

  return {
    content,
    isStreaming,
    error,
    sendMessage,
    reset,
  }
}
