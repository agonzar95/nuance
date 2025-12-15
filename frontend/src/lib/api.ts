/**
 * FE-001: Typed API Client
 *
 * Provides type-safe access to all backend API endpoints with:
 * - Automatic auth header injection
 * - Consistent error handling
 * - Request/response typing
 */

import { createClient } from '@/lib/supabase/client'
import {
  Action,
  ActionCreate,
  ActionUpdate,
  ActionListParams,
  ActionListResponse,
  ChatRequest,
  ChatResponse,
  ProcessRequest,
  RouterResponse,
  Profile,
  ProfileUpdate,
  Conversation,
  ConversationType,
  Message,
  ApiError,
  ApiErrorData,
  TranscriptionResponse,
  BreakdownResult,
} from '@/types/api'

// ============================================================================
// Configuration
// ============================================================================

interface ApiConfig {
  baseUrl: string
  getToken: () => Promise<string | null>
}

// ============================================================================
// API Client Class
// ============================================================================

class ApiClient {
  private config: ApiConfig

  constructor(config: ApiConfig) {
    this.config = config
  }

  /**
   * Make an authenticated request to the API
   */
  private async request<T>(
    method: string,
    path: string,
    options?: {
      body?: unknown
      params?: Record<string, string | number | boolean | undefined>
    }
  ): Promise<T> {
    const token = await this.config.getToken()

    // Build URL with query params
    const url = new URL(`${this.config.baseUrl}${path}`)
    if (options?.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.set(key, String(value))
        }
      })
    }

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: options?.body ? JSON.stringify(options.body) : undefined,
    })

    if (!response.ok) {
      let errorData: ApiErrorData
      try {
        errorData = await response.json()
      } catch {
        errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
      }
      throw new ApiError(response.status, errorData)
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return undefined as T
    }

    return response.json()
  }

  // ==========================================================================
  // Actions
  // ==========================================================================

  /**
   * Get list of actions with optional filters
   */
  async getActions(params?: ActionListParams): Promise<ActionListResponse> {
    const queryParams: Record<string, string | number | undefined> = {}

    if (params?.status) {
      queryParams.status = Array.isArray(params.status)
        ? params.status.join(',')
        : params.status
    }
    if (params?.planned_date) {
      queryParams.planned_date = params.planned_date
    }
    if (params?.limit) {
      queryParams.limit = params.limit
    }
    if (params?.offset) {
      queryParams.offset = params.offset
    }

    return this.request<ActionListResponse>('GET', '/api/actions', {
      params: queryParams,
    })
  }

  /**
   * Get a single action by ID
   */
  async getAction(id: string): Promise<Action> {
    return this.request<Action>('GET', `/api/actions/${id}`)
  }

  /**
   * Create a new action
   */
  async createAction(data: ActionCreate): Promise<Action> {
    return this.request<Action>('POST', '/api/actions', { body: data })
  }

  /**
   * Update an existing action
   */
  async updateAction(id: string, data: ActionUpdate): Promise<Action> {
    return this.request<Action>('PATCH', `/api/actions/${id}`, { body: data })
  }

  /**
   * Delete an action
   */
  async deleteAction(id: string): Promise<void> {
    return this.request<void>('DELETE', `/api/actions/${id}`)
  }

  /**
   * Complete an action (convenience method)
   */
  async completeAction(
    id: string,
    actualMinutes?: number
  ): Promise<Action> {
    return this.updateAction(id, {
      status: 'done',
      actual_minutes: actualMinutes,
      completed_at: new Date().toISOString(),
    })
  }

  /**
   * Plan an action for a specific date
   */
  async planAction(id: string, date: string): Promise<Action> {
    return this.updateAction(id, {
      status: 'planned',
      planned_date: date,
    })
  }

  /**
   * Move action back to inbox
   */
  async unplanAction(id: string): Promise<Action> {
    return this.updateAction(id, {
      status: 'inbox',
      planned_date: null,
    })
  }

  // ==========================================================================
  // AI / Chat
  // ==========================================================================

  /**
   * Send a chat message (non-streaming)
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('POST', '/api/ai/chat', {
      body: request,
    })
  }

  /**
   * Process a message through the intent router (non-streaming)
   */
  async process(request: ProcessRequest): Promise<RouterResponse> {
    return this.request<RouterResponse>('POST', '/api/ai/process', {
      body: request,
    })
  }

  /**
   * Get AI service status
   */
  async getAiStatus(): Promise<{
    user_id: string
    services: Record<string, string>
    rate_limit: {
      minute: { used: number; limit: number; remaining: number }
      day: { used: number; limit: number; remaining: number }
    }
  }> {
    return this.request('GET', '/api/ai/status')
  }

  /**
   * Get breakdown suggestions for a task (EXE-006)
   */
  async getBreakdown(taskTitle: string): Promise<BreakdownResult> {
    return this.request<BreakdownResult>('POST', '/api/ai/breakdown', {
      body: { task_title: taskTitle },
    })
  }

  // ==========================================================================
  // Profile
  // ==========================================================================

  /**
   * Get current user's profile
   */
  async getProfile(): Promise<Profile> {
    return this.request<Profile>('GET', '/api/profile')
  }

  /**
   * Update current user's profile
   */
  async updateProfile(data: ProfileUpdate): Promise<Profile> {
    return this.request<Profile>('PATCH', '/api/profile', { body: data })
  }

  // ==========================================================================
  // Conversations
  // ==========================================================================

  /**
   * Create a new conversation
   */
  async createConversation(type: ConversationType): Promise<Conversation> {
    return this.request<Conversation>('POST', '/api/conversations', {
      body: { type },
    })
  }

  /**
   * Get conversation messages
   */
  async getMessages(conversationId: string): Promise<Message[]> {
    return this.request<Message[]>(
      'GET',
      `/api/conversations/${conversationId}/messages`
    )
  }

  /**
   * Send a message in a conversation
   */
  async sendMessage(
    conversationId: string,
    content: string
  ): Promise<Message> {
    return this.request<Message>(
      'POST',
      `/api/conversations/${conversationId}/messages`,
      { body: { content } }
    )
  }

  // ==========================================================================
  // Transcription
  // ==========================================================================

  /**
   * Transcribe audio to text
   */
  async transcribe(audioBlob: Blob): Promise<TranscriptionResponse> {
    const token = await this.config.getToken()
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')

    const response = await fetch(`${this.config.baseUrl}/transcribe`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    })

    if (!response.ok) {
      let errorData: ApiErrorData
      try {
        errorData = await response.json()
      } catch {
        errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
      }
      throw new ApiError(response.status, errorData)
    }

    return response.json()
  }
}

// ============================================================================
// Factory & Export
// ============================================================================

let apiClientInstance: ApiClient | null = null

/**
 * Get the API client instance
 */
export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    const supabase = createClient()

    apiClientInstance = new ApiClient({
      baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      getToken: async () => {
        const {
          data: { session },
        } = await supabase.auth.getSession()
        return session?.access_token ?? null
      },
    })
  }

  return apiClientInstance
}

/**
 * Default API client instance for direct imports
 */
export const api = {
  get actions() {
    const client = getApiClient()
    return {
      list: client.getActions.bind(client),
      get: client.getAction.bind(client),
      create: client.createAction.bind(client),
      update: client.updateAction.bind(client),
      delete: client.deleteAction.bind(client),
      complete: client.completeAction.bind(client),
      plan: client.planAction.bind(client),
      unplan: client.unplanAction.bind(client),
    }
  },

  get ai() {
    const client = getApiClient()
    return {
      chat: client.chat.bind(client),
      process: client.process.bind(client),
      status: client.getAiStatus.bind(client),
      breakdown: client.getBreakdown.bind(client),
    }
  },

  get profile() {
    const client = getApiClient()
    return {
      get: client.getProfile.bind(client),
      update: client.updateProfile.bind(client),
    }
  },

  get conversations() {
    const client = getApiClient()
    return {
      create: client.createConversation.bind(client),
      messages: client.getMessages.bind(client),
      send: client.sendMessage.bind(client),
    }
  },

  get transcription() {
    const client = getApiClient()
    return {
      transcribe: client.transcribe.bind(client),
    }
  },
}

// Re-export types
export type { ApiClient }
