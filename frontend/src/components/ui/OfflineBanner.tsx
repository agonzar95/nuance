'use client'

import { useOffline } from '@/hooks/useOffline'

export function OfflineBanner() {
  const isOffline = useOffline()

  if (!isOffline) return null

  return (
    <div className="fixed top-0 left-0 right-0 bg-warning text-warning-foreground py-2 px-4 text-center text-sm z-50">
      You&apos;re offline. Changes will sync when you&apos;re back online.
    </div>
  )
}
