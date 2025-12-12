'use client'

/**
 * React Query Provider
 *
 * Wraps the app with TanStack Query's QueryClientProvider
 * for data fetching and caching.
 */

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactNode, useState } from 'react'
import { makeQueryClient } from '@/lib/query'

interface QueryProviderProps {
  children: ReactNode
}

export function QueryProvider({ children }: QueryProviderProps) {
  // Create a new QueryClient instance once per component lifecycle
  // This prevents creating a new client on every render
  const [queryClient] = useState(() => makeQueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
