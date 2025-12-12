/**
 * API Types for Nuance Frontend
 *
 * Aligned with backend models in backend/app/models/database.py
 * and API contracts in backend/app/routers/ai.py
 */

// ============================================================================
// Enums
// ============================================================================

export type ActionStatus =
  | 'inbox'
  | 'candidate'
  | 'planned'
  | 'active'
  | 'done'
  | 'dropped'
  | 'rolled'

export type ActionComplexity = 'atomic' | 'composite' | 'project'

export type ConversationType = 'capture' | 'coaching' | 'onboarding'

export type MessageRole = 'user' | 'assistant' | 'system'

export type NotificationChannel = 'email' | 'telegram' | 'both'

export type Intent = 'capture' | 'coaching' | 'command'

// ============================================================================
// Core Models
// ============================================================================

export interface Action {
  id: string
  user_id: string
  title: string
  raw_input?: string | null
  status: ActionStatus
  complexity: ActionComplexity
  avoidance_weight: number
  estimated_minutes: number
  actual_minutes?: number | null
  planned_date?: string | null
  position: number
  parent_id?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
}

export interface ActionCreate {
  title: string
  raw_input?: string
  status?: ActionStatus
  complexity?: ActionComplexity
  avoidance_weight?: number
  estimated_minutes?: number
  planned_date?: string
  parent_id?: string
}

export interface ActionUpdate {
  title?: string
  status?: ActionStatus
  complexity?: ActionComplexity
  avoidance_weight?: number
  estimated_minutes?: number
  actual_minutes?: number
  planned_date?: string | null
  completed_at?: string
  position?: number
}

export interface Profile {
  id: string
  timezone: string
  telegram_chat_id?: string | null
  notification_channel: NotificationChannel
  notification_enabled: boolean
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export interface ProfileUpdate {
  timezone?: string
  telegram_chat_id?: string
  notification_channel?: NotificationChannel
  notification_enabled?: boolean
  onboarding_completed?: boolean
}

export interface Conversation {
  id: string
  user_id: string
  type: ConversationType
  context_action_id?: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  created_at: string
}

// ============================================================================
// API Request/Response Types
// ============================================================================

// Chat
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  system?: string
}

export interface ChatResponse {
  content: string
  input_tokens: number
  output_tokens: number
}

// Process (Intent Router)
export interface ProcessRequest {
  text: string
  task_id?: string
  task_title?: string
  force_intent?: Intent
}

export interface ExtractedAction {
  title: string
  estimated_minutes: number
  raw_segment: string
}

export interface AvoidanceAnalysis {
  weight: number
  signals: string[]
  reasoning: string
}

export interface ComplexityAnalysis {
  complexity: ActionComplexity
  suggested_steps?: string[]
  needs_breakdown: boolean
}

export interface ConfidenceAnalysis {
  confidence: number
  ambiguities: string[]
  reasoning: string
}

export interface EnrichedAction {
  title: string
  estimated_minutes: number
  raw_segment: string
  avoidance: AvoidanceAnalysis
  complexity: ComplexityAnalysis
  confidence: ConfidenceAnalysis
}

export interface CaptureResult {
  actions: EnrichedAction[]
  needs_validation: boolean
  ambiguities: string[]
}

export interface CoachingResult {
  message: string
}

export interface CommandResult {
  message: string
  command: string
}

export interface RouterResponse {
  intent: Intent
  capture?: CaptureResult
  coaching?: CoachingResult
  command?: CommandResult
}

// Actions List
export interface ActionListParams {
  status?: ActionStatus | ActionStatus[]
  planned_date?: string
  limit?: number
  offset?: number
}

export interface ActionListResponse {
  actions: Action[]
  total: number
}

// ============================================================================
// Error Types
// ============================================================================

export interface ApiErrorData {
  error: string
  error_code?: string
  details?: unknown
  request_id?: string
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public data: ApiErrorData
  ) {
    super(data.error)
    this.name = 'ApiError'
  }

  get isAuthError(): boolean {
    return this.status === 401
  }

  get isRateLimited(): boolean {
    return this.status === 429
  }

  get isNotFound(): boolean {
    return this.status === 404
  }

  get isValidationError(): boolean {
    return this.status === 422
  }
}
