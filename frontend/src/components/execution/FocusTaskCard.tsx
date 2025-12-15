'use client'

import { AvoidanceIndicator } from '@/components/ui/AvoidanceIndicator'
import { SubtaskChecklist } from '@/components/execution/SubtaskChecklist'
import type { Action } from '@/types/api'

interface Subtask {
  id: string
  title: string
  completed: boolean
  order: number
}

interface FocusTaskCardProps {
  action: Action
  subtasks?: Subtask[]
  onSubtaskToggle?: (subtaskId: string, completed: boolean) => void
}

export function FocusTaskCard({
  action,
  subtasks,
  onSubtaskToggle
}: FocusTaskCardProps) {
  return (
    <div className="w-full max-w-lg space-y-6">
      {/* Main Task */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2">
          <AvoidanceIndicator
            weight={action.avoidance_weight}
            size="lg"
          />
        </div>
        <h1 className="text-2xl md:text-3xl font-semibold leading-tight">
          {action.title}
        </h1>
        {action.raw_input && action.raw_input !== action.title && (
          <p className="text-muted-foreground">{action.raw_input}</p>
        )}
      </div>

      {/* Subtasks */}
      {subtasks && subtasks.length > 0 && (
        <SubtaskChecklist
          subtasks={subtasks}
          onToggle={onSubtaskToggle}
        />
      )}

      {/* Estimate */}
      {action.estimated_minutes && (
        <p className="text-center text-sm text-muted-foreground">
          Estimated: ~{action.estimated_minutes} minutes
        </p>
      )}
    </div>
  )
}
