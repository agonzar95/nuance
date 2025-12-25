/**
 * Agent Output Contract v0 - TypeScript Types
 *
 * Standardized output contract for all agent turns, regardless of intent type.
 * Aligned with backend contracts in backend/app/contracts/agent_output_v0.py
 *
 * Contract Version: 0.1.0
 */

// =============================================================================
// Enums
// =============================================================================

export type IntentType = 'capture' | 'coaching' | 'command' | 'clarify'

export type CaptureType =
  | 'goal'
  | 'plan'
  | 'habit'
  | 'task'
  | 'reflection'
  | 'blocker'
  | 'metric'

export type IntentLayer = 'capture' | 'clarify' | 'execute' | 'reflect' | 'unknown'

export type SurvivalFunction =
  | 'maintenance'
  | 'growth'
  | 'protection'
  | 'connection'
  | 'unknown'

export type CognitiveLoadLevel = 'routine' | 'high_friction' | 'unknown'

export type TimeHorizon =
  | 'immediate'
  | 'today'
  | 'this_week'
  | 'this_month'
  | 'long_term'
  | 'unknown'

export type AgencyLevel = 'autonomous' | 'delegated' | 'blocked' | 'unknown'

export type PsychSource = 'intrinsic' | 'extrinsic' | 'avoidance' | 'unknown'

export type SystemRole =
  | 'capture'
  | 'scaffold'
  | 'track'
  | 'remind'
  | 'coach'
  | 'unknown'

export type Scope = 'atomic' | 'composite' | 'project'

export type Stage =
  | 'not_started'
  | 'in_progress'
  | 'blocked'
  | 'waiting'
  | 'done'
  | 'unknown'

export type EnergyLevel = 'low' | 'medium' | 'high' | 'unknown'

export type EntityType = 'action' | 'conversation' | 'message' | 'profile'

export type Operation = 'created' | 'updated' | 'deleted'

export type QuestionType = 'scope' | 'timeline' | 'priority' | 'blocker' | 'other'

export type UIBlockType =
  | 'capture_list'
  | 'breakdown_steps'
  | 'coaching_message'
  | 'insight_card'
  | 'question_prompt'
  | 'command_result'

// =============================================================================
// Taxonomy & Inference Models
// =============================================================================

export interface TaxonomyLayer {
  intent_layer: IntentLayer
  survival_function: SurvivalFunction
  cognitive_load: CognitiveLoadLevel
  time_horizon: TimeHorizon
  agency_level: AgencyLevel
  psych_source: PsychSource
  system_role: SystemRole
}

export interface MagnitudeInference {
  scope: Scope
  complexity: number // 1-5
  dependencies: number
  uncertainty: number // 0-1
}

export interface StateInference {
  stage: Stage
  bottleneck?: string | null
  energy_required: EnergyLevel
}

// =============================================================================
// Core Output Models
// =============================================================================

export interface Capture {
  id: string
  type: CaptureType
  title: string
  raw_segment: string
  estimated_minutes: number
  avoidance_weight: number // 1-5
  confidence: number // 0-1
  ambiguities: string[]
  labels?: TaxonomyLayer | null
  magnitude?: MagnitudeInference | null
  state?: StateInference | null
  needs_breakdown: boolean
}

export interface AtomicTask {
  id: string
  parent_capture_id?: string | null
  verb: string
  object: string
  full_description?: string | null
  definition_of_done?: string | null
  estimated_minutes: number // 1-30
  energy_level: EnergyLevel
  prerequisites: string[]
  is_first_action: boolean
  is_physical: boolean
}

export interface StateUpdate {
  entity_type: EntityType
  entity_id?: string | null
  temp_id?: string | null
  operation: Operation
  changes?: Record<string, unknown> | null
}

export interface ClarificationQuestion {
  id: string
  question: string
  target_capture_id: string
  question_type: QuestionType
  suggested_answers: string[]
}

export interface UIBlock {
  type: UIBlockType
  data: Record<string, unknown>
  priority: number
}

export interface ContractPsychologicalInsight {
  pattern_name: string
  description: string
  suggested_strategy: string
  confidence: number
}

export interface ContractCommandResult {
  command: string
  message: string
  data?: Record<string, unknown> | null
}

// =============================================================================
// Intent Classification
// =============================================================================

export interface IntentClassification {
  type: IntentType
  confidence: number
  reasoning?: string | null
}

// =============================================================================
// Provenance
// =============================================================================

export interface ContractTokenUsage {
  input_tokens: number
  output_tokens: number
}

export interface Provenance {
  model_id?: string | null
  prompt_versions: Record<string, string>
  processing_time_ms: number
  token_usage?: ContractTokenUsage | null
}

// =============================================================================
// Agent Output
// =============================================================================

export interface AgentOutput {
  raw_input: string
  captures: Capture[]
  atomic_tasks: AtomicTask[]
  state_updates: StateUpdate[]
  questions: ClarificationQuestion[]
  insights: ContractPsychologicalInsight[]
  coaching_message?: string | null
  command_result?: ContractCommandResult | null
  user_facing_summary?: string | null
  ui_blocks: UIBlock[]
  overall_confidence: number
  cognitive_load: CognitiveLoadLevel
  needs_scaffolding: boolean
  scaffolding_question?: string | null
}

// =============================================================================
// Top-Level Contract
// =============================================================================

export interface AgentOutputContract {
  contract_version: string
  request_id: string
  trace_id?: string | null
  timestamp: string // ISO 8601 datetime
  intent: IntentClassification
  output: AgentOutput
  provenance?: Provenance | null
}

// =============================================================================
// Contract Version Constant
// =============================================================================

export const CONTRACT_VERSION = '0.1.0'

// =============================================================================
// Type Guards
// =============================================================================

export function isAgentOutputContract(obj: unknown): obj is AgentOutputContract {
  if (typeof obj !== 'object' || obj === null) return false
  const contract = obj as AgentOutputContract
  return (
    typeof contract.contract_version === 'string' &&
    typeof contract.request_id === 'string' &&
    typeof contract.timestamp === 'string' &&
    typeof contract.intent === 'object' &&
    typeof contract.output === 'object'
  )
}

export function hasContractVersion(obj: unknown): boolean {
  if (typeof obj !== 'object' || obj === null) return false
  return 'contract_version' in obj
}
