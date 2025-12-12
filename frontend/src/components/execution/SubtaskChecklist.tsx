'use client'

import { cn } from '@/lib/utils'

interface Subtask {
  id: string
  title: string
  completed: boolean
  order: number
}

interface SubtaskChecklistProps {
  subtasks: Subtask[]
  onToggle?: (subtaskId: string, completed: boolean) => void
}

export function SubtaskChecklist({
  subtasks,
  onToggle
}: SubtaskChecklistProps) {
  const sortedSubtasks = [...subtasks].sort((a, b) => a.order - b.order)
  const completedCount = subtasks.filter(s => s.completed).length

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">Steps</span>
        <span className="text-muted-foreground">
          {completedCount}/{subtasks.length} done
        </span>
      </div>

      <div className="space-y-2">
        {sortedSubtasks.map((subtask) => (
          <label
            key={subtask.id}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <input
              type="checkbox"
              checked={subtask.completed}
              onChange={(e) => onToggle?.(subtask.id, e.target.checked)}
              className="sr-only"
            />
            <div
              className={cn(
                'w-5 h-5 rounded-full border-2 flex items-center justify-center',
                'transition-colors',
                subtask.completed
                  ? 'bg-primary border-primary'
                  : 'border-muted-foreground group-hover:border-primary'
              )}
            >
              {subtask.completed && (
                <CheckIcon className="w-3 h-3 text-primary-foreground" />
              )}
            </div>
            <span
              className={cn(
                'transition-all',
                subtask.completed && 'line-through text-muted-foreground'
              )}
            >
              {subtask.title}
            </span>
          </label>
        ))}
      </div>
    </div>
  )
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}
