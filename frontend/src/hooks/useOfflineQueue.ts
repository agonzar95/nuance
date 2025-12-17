'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useOffline } from './useOffline'

/**
 * PWA-003: Offline Mutation Queue
 *
 * Queues failed mutations when offline and retries them when back online.
 * Uses localStorage for persistence across sessions.
 */

export interface QueuedMutation {
  id: string
  timestamp: number
  type: 'create' | 'update' | 'delete'
  endpoint: string
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  retryCount: number
  maxRetries: number
}

interface OfflineQueueState {
  queue: QueuedMutation[]
  isProcessing: boolean
  lastSyncAt: number | null
}

const STORAGE_KEY = 'nuance-offline-queue'
const MAX_RETRIES = 3
const RETRY_DELAY_MS = 1000

// Generate unique ID for queue items
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Load queue from localStorage
function loadQueue(): QueuedMutation[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.warn('Failed to load offline queue:', e)
  }
  return []
}

// Save queue to localStorage
function saveQueue(queue: QueuedMutation[]): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queue))
  } catch (e) {
    console.warn('Failed to save offline queue:', e)
  }
}

export function useOfflineQueue() {
  const isOffline = useOffline()
  const [state, setState] = useState<OfflineQueueState>({
    queue: [],
    isProcessing: false,
    lastSyncAt: null,
  })
  const processingRef = useRef(false)

  // Load queue on mount
  useEffect(() => {
    const savedQueue = loadQueue()
    if (savedQueue.length > 0) {
      setState(prev => ({ ...prev, queue: savedQueue }))
    }
  }, [])

  // Save queue whenever it changes
  useEffect(() => {
    saveQueue(state.queue)
  }, [state.queue])

  // Add mutation to queue
  const enqueue = useCallback((
    mutation: Omit<QueuedMutation, 'id' | 'timestamp' | 'retryCount' | 'maxRetries'>
  ): string => {
    const id = generateId()
    const queuedMutation: QueuedMutation = {
      ...mutation,
      id,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: MAX_RETRIES,
    }

    setState(prev => ({
      ...prev,
      queue: [...prev.queue, queuedMutation],
    }))

    return id
  }, [])

  // Remove mutation from queue
  const dequeue = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      queue: prev.queue.filter(m => m.id !== id),
    }))
  }, [])

  // Process a single mutation
  const processMutation = useCallback(async (
    mutation: QueuedMutation,
    getToken: () => Promise<string | null>
  ): Promise<boolean> => {
    try {
      const token = await getToken()
      const response = await fetch(mutation.endpoint, {
        method: mutation.method,
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: mutation.body ? JSON.stringify(mutation.body) : undefined,
      })

      if (response.ok) {
        return true
      }

      // Don't retry on client errors (4xx), except 429 (rate limit)
      if (response.status >= 400 && response.status < 500 && response.status !== 429) {
        console.warn(`Mutation ${mutation.id} failed with ${response.status}, not retrying`)
        return true // Remove from queue
      }

      return false
    } catch (e) {
      console.warn(`Mutation ${mutation.id} failed:`, e)
      return false
    }
  }, [])

  // Process all queued mutations
  const processQueue = useCallback(async (
    getToken: () => Promise<string | null>
  ) => {
    if (processingRef.current || state.queue.length === 0 || isOffline) {
      return
    }

    processingRef.current = true
    setState(prev => ({ ...prev, isProcessing: true }))

    const toProcess = [...state.queue]
    const processed: string[] = []
    const failed: QueuedMutation[] = []

    for (const mutation of toProcess) {
      const success = await processMutation(mutation, getToken)

      if (success) {
        processed.push(mutation.id)
      } else if (mutation.retryCount < mutation.maxRetries) {
        failed.push({
          ...mutation,
          retryCount: mutation.retryCount + 1,
        })
        // Add delay between retries
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS))
      } else {
        // Max retries exceeded, remove from queue
        console.warn(`Mutation ${mutation.id} exceeded max retries, removing from queue`)
        processed.push(mutation.id)
      }
    }

    setState(prev => ({
      ...prev,
      queue: prev.queue
        .filter(m => !processed.includes(m.id))
        .map(m => {
          const failedItem = failed.find(f => f.id === m.id)
          return failedItem || m
        }),
      isProcessing: false,
      lastSyncAt: Date.now(),
    }))

    processingRef.current = false
  }, [state.queue, isOffline, processMutation])

  // Auto-process when coming back online
  useEffect(() => {
    if (!isOffline && state.queue.length > 0 && !processingRef.current) {
      // Small delay to ensure network is stable
      const timeout = setTimeout(() => {
        // Note: Consumer must call processQueue with their token getter
      }, 1000)
      return () => clearTimeout(timeout)
    }
  }, [isOffline, state.queue.length])

  // Clear all queued mutations
  const clearQueue = useCallback(() => {
    setState(prev => ({ ...prev, queue: [] }))
  }, [])

  // Get queue size
  const queueSize = state.queue.length

  // Check if a specific mutation is queued
  const isQueued = useCallback((id: string) => {
    return state.queue.some(m => m.id === id)
  }, [state.queue])

  return {
    queue: state.queue,
    queueSize,
    isProcessing: state.isProcessing,
    lastSyncAt: state.lastSyncAt,
    isOffline,
    enqueue,
    dequeue,
    processQueue,
    clearQueue,
    isQueued,
  }
}

/**
 * Hook for mutations that automatically queue when offline
 */
export function useOfflineMutation<TData, TVariables>(config: {
  mutationFn: (variables: TVariables) => Promise<TData>
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (error: Error, variables: TVariables) => void
  onOfflineQueue?: (id: string, variables: TVariables) => void
  endpoint: string
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  type: 'create' | 'update' | 'delete'
}) {
  const { isOffline, enqueue } = useOfflineQueue()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const mutate = useCallback(async (variables: TVariables) => {
    setIsLoading(true)
    setError(null)

    // If offline, queue the mutation
    if (isOffline) {
      const id = enqueue({
        type: config.type,
        endpoint: config.endpoint,
        method: config.method,
        body: variables,
      })
      config.onOfflineQueue?.(id, variables)
      setIsLoading(false)
      return
    }

    // If online, execute immediately
    try {
      const data = await config.mutationFn(variables)
      config.onSuccess?.(data, variables)
      setIsLoading(false)
      return data
    } catch (e) {
      const err = e instanceof Error ? e : new Error('Unknown error')
      setError(err)
      config.onError?.(err, variables)
      setIsLoading(false)
      throw err
    }
  }, [isOffline, enqueue, config])

  return {
    mutate,
    isLoading,
    error,
    isOffline,
  }
}
