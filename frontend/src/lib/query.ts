/**
 * React Query Configuration
 *
 * Sets up TanStack Query with appropriate defaults for Nuance.
 */

import { QueryClient } from '@tanstack/react-query'

/**
 * Create a configured QueryClient instance
 */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Stale time: how long data is considered fresh (5 minutes)
        staleTime: 5 * 60 * 1000,
        // Cache time: how long to keep unused data in cache (30 minutes)
        gcTime: 30 * 60 * 1000,
        // Retry failed queries 1 time
        retry: 1,
        // Don't refetch on window focus by default (can be enabled per query)
        refetchOnWindowFocus: false,
      },
      mutations: {
        // Retry failed mutations once
        retry: 1,
      },
    },
  })
}

// Singleton query client for client-side usage
let browserQueryClient: QueryClient | undefined = undefined

/**
 * Get the QueryClient instance.
 * On the server, creates a new instance each time.
 * On the client, reuses the same instance.
 */
export function getQueryClient(): QueryClient {
  if (typeof window === 'undefined') {
    // Server: always create a new query client
    return makeQueryClient()
  }

  // Browser: reuse the same client
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient()
  }
  return browserQueryClient
}

// ============================================================================
// Query Keys
// ============================================================================

/**
 * Centralized query key factories for consistency
 */
export const queryKeys = {
  // Actions
  actions: {
    all: ['actions'] as const,
    lists: () => [...queryKeys.actions.all, 'list'] as const,
    list: (filters: object) =>
      [...queryKeys.actions.lists(), filters] as const,
    details: () => [...queryKeys.actions.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.actions.details(), id] as const,
    inbox: () => queryKeys.actions.list({ status: 'inbox' }),
    today: (date: string) => queryKeys.actions.list({ planned_date: date }),
  },

  // Profile
  profile: {
    all: ['profile'] as const,
    current: () => [...queryKeys.profile.all, 'current'] as const,
  },

  // Conversations
  conversations: {
    all: ['conversations'] as const,
    messages: (id: string) =>
      [...queryKeys.conversations.all, id, 'messages'] as const,
  },

  // AI
  ai: {
    status: ['ai', 'status'] as const,
  },
} as const
