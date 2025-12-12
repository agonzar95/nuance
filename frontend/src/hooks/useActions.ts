'use client'

/**
 * Action Hooks
 *
 * React Query hooks for action CRUD operations.
 * Part of FE-001: API Client integration.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'
import type {
  Action,
  ActionCreate,
  ActionUpdate,
  ActionListParams,
} from '@/types/api'

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Fetch actions with optional filters
 */
export function useActions(params?: ActionListParams) {
  return useQuery({
    queryKey: queryKeys.actions.list(params ?? {}),
    queryFn: () => api.actions.list(params),
  })
}

/**
 * Fetch inbox actions
 */
export function useInboxActions() {
  return useQuery({
    queryKey: queryKeys.actions.inbox(),
    queryFn: () => api.actions.list({ status: 'inbox' }),
  })
}

/**
 * Fetch today's planned actions
 */
export function useTodayActions(date?: string) {
  const today = date ?? new Date().toISOString().split('T')[0]
  return useQuery({
    queryKey: queryKeys.actions.today(today),
    queryFn: () => api.actions.list({ planned_date: today }),
  })
}

/**
 * Fetch a single action by ID
 */
export function useAction(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.actions.detail(id!),
    queryFn: () => api.actions.get(id!),
    enabled: !!id,
  })
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Create a new action
 */
export function useCreateAction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ActionCreate) => api.actions.create(data),
    onSuccess: () => {
      // Invalidate all action queries to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })
}

/**
 * Update an existing action
 */
export function useUpdateAction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ActionUpdate }) =>
      api.actions.update(id, data),
    onSuccess: (updatedAction) => {
      // Update the specific action in cache
      queryClient.setQueryData(
        queryKeys.actions.detail(updatedAction.id),
        updatedAction
      )
      // Invalidate list queries as status/date may have changed
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Delete an action
 */
export function useDeleteAction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.actions.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: queryKeys.actions.detail(deletedId),
      })
      // Invalidate list queries
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Complete an action
 */
export function useCompleteAction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      actualMinutes,
    }: {
      id: string
      actualMinutes?: number
    }) => api.actions.complete(id, actualMinutes),
    onSuccess: (updatedAction) => {
      queryClient.setQueryData(
        queryKeys.actions.detail(updatedAction.id),
        updatedAction
      )
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Plan an action for a specific date
 */
export function usePlanAction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, date }: { id: string; date: string }) =>
      api.actions.plan(id, date),
    onSuccess: (updatedAction) => {
      queryClient.setQueryData(
        queryKeys.actions.detail(updatedAction.id),
        updatedAction
      )
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

/**
 * Unplan an action (move back to inbox)
 */
export function useUnplanAction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.actions.unplan(id),
    onSuccess: (updatedAction) => {
      queryClient.setQueryData(
        queryKeys.actions.detail(updatedAction.id),
        updatedAction
      )
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.lists() })
    },
  })
}

// ============================================================================
// Utility Types
// ============================================================================

export type { Action, ActionCreate, ActionUpdate, ActionListParams }
