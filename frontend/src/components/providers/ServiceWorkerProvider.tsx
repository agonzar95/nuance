'use client'

/**
 * FE-013: Service Worker Registration
 *
 * Registers the service worker on mount and handles updates.
 */

import { useEffect, useState, createContext, useContext, ReactNode } from 'react'

// ============================================================================
// Types
// ============================================================================

interface ServiceWorkerContextValue {
  /** Whether a service worker is registered */
  isRegistered: boolean
  /** Whether an update is available */
  hasUpdate: boolean
  /** Apply the pending update (reloads page) */
  applyUpdate: () => void
}

// ============================================================================
// Context
// ============================================================================

const ServiceWorkerContext = createContext<ServiceWorkerContextValue>({
  isRegistered: false,
  hasUpdate: false,
  applyUpdate: () => {},
})

export function useServiceWorker() {
  return useContext(ServiceWorkerContext)
}

// ============================================================================
// Provider
// ============================================================================

interface ServiceWorkerProviderProps {
  children: ReactNode
}

export function ServiceWorkerProvider({ children }: ServiceWorkerProviderProps) {
  const [isRegistered, setIsRegistered] = useState(false)
  const [hasUpdate, setHasUpdate] = useState(false)
  const [waitingWorker, setWaitingWorker] = useState<ServiceWorker | null>(null)

  useEffect(() => {
    // Only register in production or if explicitly enabled
    if (
      typeof window === 'undefined' ||
      !('serviceWorker' in navigator) ||
      globalThis.process?.env?.NODE_ENV === 'development'
    ) {
      return
    }

    const registerServiceWorker = async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/',
        })

        setIsRegistered(true)

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          if (!newWorker) return

          newWorker.addEventListener('statechange', () => {
            if (
              newWorker.state === 'installed' &&
              navigator.serviceWorker.controller
            ) {
              // New version available
              setHasUpdate(true)
              setWaitingWorker(newWorker)
            }
          })
        })

        // If there's already a waiting worker (from previous visit)
        if (registration.waiting) {
          setHasUpdate(true)
          setWaitingWorker(registration.waiting)
        }

        // Handle controller change (after skipWaiting)
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          window.location.reload()
        })
      } catch (error) {
        console.error('Service worker registration failed:', error)
      }
    }

    registerServiceWorker()
  }, [])

  const applyUpdate = () => {
    if (waitingWorker) {
      waitingWorker.postMessage('skipWaiting')
    }
  }

  return (
    <ServiceWorkerContext.Provider value={{ isRegistered, hasUpdate, applyUpdate }}>
      {children}
    </ServiceWorkerContext.Provider>
  )
}

// ============================================================================
// Update Banner Component
// ============================================================================

export function UpdateAvailableBanner() {
  const { hasUpdate, applyUpdate } = useServiceWorker()

  if (!hasUpdate) return null

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80 bg-primary text-primary-foreground p-4 rounded-lg shadow-lg z-50">
      <p className="text-sm font-medium mb-2">Update available</p>
      <p className="text-xs opacity-90 mb-3">
        A new version of Nuance is ready. Refresh to get the latest features.
      </p>
      <div className="flex gap-2">
        <button
          onClick={applyUpdate}
          className="px-3 py-1.5 bg-primary-foreground text-primary rounded text-sm font-medium hover:opacity-90"
        >
          Refresh now
        </button>
        <button
          onClick={() => {
            // Dismiss by hiding the parent (handled via CSS/state)
          }}
          className="px-3 py-1.5 text-sm opacity-75 hover:opacity-100"
        >
          Later
        </button>
      </div>
    </div>
  )
}
