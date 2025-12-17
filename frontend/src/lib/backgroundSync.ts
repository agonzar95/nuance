/**
 * PWA-003: Background Sync Utilities
 *
 * Registers for background sync when available, falling back to
 * online event listener for older browsers.
 */

const SYNC_TAG = 'nuance-offline-sync'

/**
 * Check if background sync is supported
 */
export function isBackgroundSyncSupported(): boolean {
  return (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    'SyncManager' in window
  )
}

/**
 * Register for background sync
 * This tells the service worker to sync queued mutations when online
 */
export async function registerBackgroundSync(): Promise<boolean> {
  if (!isBackgroundSyncSupported()) {
    return false
  }

  try {
    const registration = await navigator.serviceWorker.ready
    // @ts-expect-error - SyncManager types not fully available
    await registration.sync.register(SYNC_TAG)
    return true
  } catch (e) {
    console.warn('Background sync registration failed:', e)
    return false
  }
}

/**
 * Request a sync for queued mutations
 * Call this when adding items to the offline queue
 */
export async function requestSync(): Promise<void> {
  if (isBackgroundSyncSupported()) {
    await registerBackgroundSync()
  }
}

/**
 * Get the sync tag used by service worker
 */
export function getSyncTag(): string {
  return SYNC_TAG
}
