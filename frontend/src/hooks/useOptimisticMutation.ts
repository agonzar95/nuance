'use client'

/**
 * FE-002: Optimistic Updates Hook
 *
 * Provides optimistic update patterns for React Query mutations.
 * Updates UI immediately on user action, then reconciles with server response.
 * Rolls back on error.
 */

import { useMutation, useQueryClient, QueryKey } from '@tanstack/react-query'

// ============================================================================
// Generic Optimistic Mutation Hook
// ============================================================================

interface OptimisticConfig<TData, TVariables, TContext = unknown> {
  /** The function to call for the mutation */
  mutationFn: (variables: TVariables) => Promise<TData>
  /** Query key(s) to update optimistically */
  queryKey: QueryKey
  /** Function to optimistically update the cache */
  optimisticUpdate: (
    old: TData[] | undefined,
    variables: TVariables
  ) => TData[]
  /** Optional callback on error */
  onError?: (error: Error, variables: TVariables, context: TContext | undefined) => void
  /** Optional callback on success */
  onSuccess?: (data: TData, variables: TVariables, context: TContext | undefined) => void
}

/**
 * Create an optimistic mutation that updates the UI immediately.
 *
 * @example
 * ```tsx
 * const completeAction = useOptimisticMutation({
 *   mutationFn: (id: string) => api.actions.complete(id),
 *   queryKey: ['actions', 'list', { status: 'planned' }],
 *   optimisticUpdate: (actions, id) =>
 *     actions?.map(a => a.id === id ? { ...a, status: 'done' } : a) ?? [],
 *   onError: () => toast.error('Failed to complete action')
 * })
 * ```
 */
export function useOptimisticMutation<TData, TVariables>(
  config: OptimisticConfig<TData, TVariables, { previous: TData[] | undefined }>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: config.mutationFn,

    onMutate: async (variables) => {
      // Cancel any outgoing refetches to prevent optimistic update from being overwritten
      await queryClient.cancelQueries({ queryKey: config.queryKey })

      // Snapshot the previous value
      const previous = queryClient.getQueryData<TData[]>(config.queryKey)

      // Optimistically update to the new value
      queryClient.setQueryData<TData[]>(
        config.queryKey,
        (old) => config.optimisticUpdate(old, variables)
      )

      // Return context with the snapshot
      return { previous }
    },

    onError: (error, variables, context) => {
      // Roll back to the previous value on error
      if (context?.previous !== undefined) {
        queryClient.setQueryData(config.queryKey, context.previous)
      }
      config.onError?.(error as Error, variables, context)
    },

    onSuccess: (data, variables, context) => {
      config.onSuccess?.(data, variables, context)
    },

    onSettled: () => {
      // Always refetch after error or success to ensure consistency
      queryClient.invalidateQueries({ queryKey: config.queryKey })
    },
  })
}

// ============================================================================
// Pre-built Optimistic Action Hooks
// ============================================================================

import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'
import type { Action, ActionUpdate } from '@/types/api'

/**
 * Optimistic action completion
 */
export function useOptimisticCompleteAction(onError?: () => void) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, actualMinutes }: { id: string; actualMinutes?: number }) =>
      api.actions.complete(id, actualMinutes),

    onMutate: async ({ id }) => {
      // Cancel queries and snapshot
      await queryClient.cancelQueries({ queryKey: queryKeys.actions.lists() })
      const previousLists = queryClient.getQueriesData({ queryKey: queryKeys.actions.lists() })

      // Optimistically mark as done in all list caches
      queryClient.setQueriesData<{ actions: Action[] }>(
        { queryKey: queryKeys.actions.lists() },
        (old) => {
          if (!old?.actions) return old
          return {
            ...old,
            actions: old.actions.map((a) =>
              a.id === id ? { ...a, status: 'done' as const } : a
            ),
          }
        }
      )

      return { previousLists }
    },

    onError: (_, __, context) => {
      // Restore all previous list data
      context?.previousLists.forEach(([queryKey, data]) => {
        queryClient.setQueryData(queryKey, data)
      })
      onError?.()
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Optimistic action status update
 */
export function useOptimisticUpdateAction(onError?: () => void) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ActionUpdate }) =>
      api.actions.update(id, data),

    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.actions.lists() })
      const previousLists = queryClient.getQueriesData({ queryKey: queryKeys.actions.lists() })

      // Optimistically update in all list caches
      queryClient.setQueriesData<{ actions: Action[] }>(
        { queryKey: queryKeys.actions.lists() },
        (old) => {
          if (!old?.actions) return old
          return {
            ...old,
            actions: old.actions.map((a) =>
              a.id === id ? { ...a, ...data } : a
            ),
          }
        }
      )

      return { previousLists }
    },

    onError: (_, __, context) => {
      context?.previousLists.forEach(([queryKey, queryData]) => {
        queryClient.setQueryData(queryKey, queryData)
      })
      onError?.()
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Optimistic action deletion
 */
export function useOptimisticDeleteAction(onError?: () => void) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.actions.delete(id),

    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.actions.lists() })
      const previousLists = queryClient.getQueriesData({ queryKey: queryKeys.actions.lists() })

      // Optimistically remove from all list caches
      queryClient.setQueriesData<{ actions: Action[] }>(
        { queryKey: queryKeys.actions.lists() },
        (old) => {
          if (!old?.actions) return old
          return {
            ...old,
            actions: old.actions.filter((a) => a.id !== id),
          }
        }
      )

      return { previousLists }
    },

    onError: (_, __, context) => {
      context?.previousLists.forEach(([queryKey, data]) => {
        queryClient.setQueryData(queryKey, data)
      })
      onError?.()
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Optimistic action reordering (for drag-and-drop)
 */
export function useOptimisticReorderActions(onError?: () => void) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (updates: Array<{ id: string; position: number }>) =>
      Promise.all(updates.map((u) => api.actions.update(u.id, { position: u.position }))),

    onMutate: async (updates) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.actions.lists() })
      const previousLists = queryClient.getQueriesData({ queryKey: queryKeys.actions.lists() })

      // Apply position updates optimistically
      const positionMap = new Map(updates.map((u) => [u.id, u.position]))

      queryClient.setQueriesData<{ actions: Action[] }>(
        { queryKey: queryKeys.actions.lists() },
        (old) => {
          if (!old?.actions) return old
          return {
            ...old,
            actions: old.actions
              .map((a) => ({
                ...a,
                position: positionMap.get(a.id) ?? a.position,
              }))
              .sort((a, b) => a.position - b.position),
          }
        }
      )

      return { previousLists }
    },

    onError: (_, __, context) => {
      context?.previousLists.forEach(([queryKey, data]) => {
        queryClient.setQueryData(queryKey, data)
      })
      onError?.()
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}
