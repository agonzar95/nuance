/**
 * Hooks Index
 *
 * Export all hooks from a single entry point.
 */

// Action hooks (FE-001)
export {
  useActions,
  useInboxActions,
  useTodayActions,
  useAction,
  useCreateAction,
  useUpdateAction,
  useDeleteAction,
  useCompleteAction,
  usePlanAction,
  useUnplanAction,
} from './useActions'

// Optimistic mutation hooks (FE-002)
export {
  useOptimisticMutation,
  useOptimisticCompleteAction,
  useOptimisticUpdateAction,
  useOptimisticDeleteAction,
  useOptimisticReorderActions,
} from './useOptimisticMutation'

// SSE hooks (FE-003)
export {
  useSSE,
  useProcessStream,
  useChatStream,
} from './useSSE'

// Real-time sync hooks (FE-004)
export {
  useRealtimeSync,
  useRealtimeTodayActions,
  useRealtimeInboxActions,
} from './useRealtimeSync'

// Legacy real-time hooks (SUB-013)
export {
  useRealtimeActions,
  useRealtimeProfile,
} from './useRealtimeActions'

// Session hooks
export {
  useSession,
  useRequireAuth,
  useRedirectIfAuthenticated,
} from './useSession'

// Profile hooks
export { useProfile } from './useProfile'

// Offline hooks (FE-011, PWA-003)
export { useOffline } from './useOffline'
export {
  useOfflineQueue,
  useOfflineMutation,
  type QueuedMutation,
} from './useOfflineQueue'
