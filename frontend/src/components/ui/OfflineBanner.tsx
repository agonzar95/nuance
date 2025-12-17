'use client'

import { useOffline } from '@/hooks/useOffline'
import { useOfflineQueue } from '@/hooks/useOfflineQueue'

/**
 * PWA-003: Enhanced Offline Banner
 *
 * Shows offline status and queue information when disconnected.
 * Displays syncing status when processing queued mutations.
 */
export function OfflineBanner() {
  const isOffline = useOffline()
  const { queueSize, isProcessing } = useOfflineQueue()

  // Show syncing status when processing
  if (isProcessing) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-primary text-primary-foreground py-2 px-4 text-center text-sm z-50">
        <span className="inline-flex items-center gap-2">
          <span className="animate-spin inline-block w-3 h-3 border-2 border-current border-t-transparent rounded-full" />
          Syncing {queueSize} pending {queueSize === 1 ? 'change' : 'changes'}...
        </span>
      </div>
    )
  }

  // Show offline status with queue info
  if (isOffline) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-warning text-warning-foreground py-2 px-4 text-center text-sm z-50">
        You&apos;re offline.
        {queueSize > 0 ? (
          <span>
            {' '}
            {queueSize} {queueSize === 1 ? 'change' : 'changes'} will sync when
            you&apos;re back online.
          </span>
        ) : (
          <span> Changes will sync when you&apos;re back online.</span>
        )}
      </div>
    )
  }

  return null
}
