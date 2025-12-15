'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Skeleton } from '@/components/ui/Loading'
import { queryKeys } from '@/lib/query'

interface FirstStepSuggestionsProps {
  taskTitle: string
  onSelectSuggestion: (suggestion: string) => void
  onTypeOwn: () => void
}

/**
 * Displays AI-generated first step suggestions for complex tasks.
 * Helps users overcome paralysis by providing concrete starting points.
 */
export function FirstStepSuggestions({
  taskTitle,
  onSelectSuggestion,
  onTypeOwn
}: FirstStepSuggestionsProps) {
  const { data: breakdown, isLoading, error } = useQuery({
    queryKey: queryKeys.breakdown(taskTitle),
    queryFn: () => api.ai.breakdown(taskTitle),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <p className="text-muted-foreground text-center">
          Thinking of ways to start...
        </p>
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-16 w-full rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-muted-foreground">
          Couldn't generate suggestions right now.
        </p>
        <button
          onClick={onTypeOwn}
          className="px-4 py-2 text-sm text-primary hover:underline"
        >
          Type your own first step
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="text-center space-y-1">
        <p className="text-muted-foreground">
          Here are some ways to start:
        </p>
        {breakdown?.first_step_emphasis && (
          <p className="text-xs text-muted-foreground/70 italic">
            {breakdown.first_step_emphasis}
          </p>
        )}
      </div>

      <div className="space-y-2">
        {breakdown?.steps.map((step, i) => (
          <button
            key={i}
            onClick={() => onSelectSuggestion(step.title)}
            className="w-full p-4 text-left rounded-lg border hover:bg-muted transition-colors group"
          >
            <div className="flex items-start justify-between gap-2">
              <span className="flex-1">{step.title}</span>
              <span className="text-xs text-muted-foreground whitespace-nowrap">
                ~{step.estimated_minutes} min
              </span>
            </div>
          </button>
        ))}
      </div>

      <button
        onClick={onTypeOwn}
        className="w-full py-3 text-muted-foreground hover:text-foreground transition-colors"
      >
        I have my own idea
      </button>
    </div>
  )
}
