'use client'

import {
  createContext,
  useContext,
  useEffect,
  useCallback,
  ReactNode,
} from 'react'
import { useOfflineQueue, QueuedMutation } from '@/hooks/useOfflineQueue'
import { useOffline } from '@/hooks/useOffline'
import { requestSync } from '@/lib/backgroundSync'
import { createClient } from '@/lib/supabase/client'

/**
 * PWA-003: Offline Queue Provider
 *
 * Provides offline queue functionality to the app and handles:
 * - Auto-sync when coming back online
 * - Service worker message handling
 * - Queue status for UI display
 */

interface OfflineQueueContextValue {
  queue: QueuedMutation[]
  queueSize: number
  isProcessing: boolean
  isOffline: boolean
  lastSyncAt: number | null
  enqueueAction: (
    type: 'create' | 'update' | 'delete',
    endpoint: string,
    method: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    body?: unknown
  ) => string
  processQueue: () => Promise<void>
  clearQueue: () => void
}

const OfflineQueueContext = createContext<OfflineQueueContextValue | null>(null)

export function useOfflineQueueContext() {
  const context = useContext(OfflineQueueContext)
  if (!context) {
    throw new Error(
      'useOfflineQueueContext must be used within OfflineQueueProvider'
    )
  }
  return context
}

interface OfflineQueueProviderProps {
  children: ReactNode
}

export function OfflineQueueProvider({ children }: OfflineQueueProviderProps) {
  const isOffline = useOffline()
  const {
    queue,
    queueSize,
    isProcessing,
    lastSyncAt,
    enqueue,
    processQueue: processQueueInternal,
    clearQueue,
  } = useOfflineQueue()

  // Get auth token for queue processing
  const getToken = useCallback(async (): Promise<string | null> => {
    const supabase = createClient()
    const {
      data: { session },
    } = await supabase.auth.getSession()
    return session?.access_token ?? null
  }, [])

  // Process queue with auth
  const processQueue = useCallback(async () => {
    await processQueueInternal(getToken)
  }, [processQueueInternal, getToken])

  // Enqueue helper
  const enqueueAction = useCallback(
    (
      type: 'create' | 'update' | 'delete',
      endpoint: string,
      method: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
      body?: unknown
    ): string => {
      const id = enqueue({ type, endpoint, method, body })
      // Request background sync
      requestSync()
      return id
    },
    [enqueue]
  )

  // Listen for service worker messages
  useEffect(() => {
    if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) {
      return
    }

    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'PROCESS_OFFLINE_QUEUE') {
        processQueue()
      }
    }

    navigator.serviceWorker.addEventListener('message', handleMessage)

    return () => {
      navigator.serviceWorker.removeEventListener('message', handleMessage)
    }
  }, [processQueue])

  // Auto-process queue when coming back online
  useEffect(() => {
    if (!isOffline && queueSize > 0) {
      // Small delay to ensure network is stable
      const timeout = setTimeout(() => {
        processQueue()
      }, 2000)
      return () => clearTimeout(timeout)
    }
  }, [isOffline, queueSize, processQueue])

  const value: OfflineQueueContextValue = {
    queue,
    queueSize,
    isProcessing,
    isOffline,
    lastSyncAt,
    enqueueAction,
    processQueue,
    clearQueue,
  }

  return (
    <OfflineQueueContext.Provider value={value}>
      {children}
    </OfflineQueueContext.Provider>
  )
}
