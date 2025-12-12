import { cn } from '@/lib/utils'

interface TimeBudgetProps {
  plannedMinutes: number
  targetMinutes?: number // Default 480 (8 hours)
}

export function TimeBudget({
  plannedMinutes,
  targetMinutes = 480
}: TimeBudgetProps) {
  const percentage = Math.min(100, (plannedMinutes / targetMinutes) * 100)

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours === 0) return `${mins}m`
    if (mins === 0) return `${hours}h`
    return `${hours}h ${mins}m`
  }

  const getColor = () => {
    if (percentage <= 70) return 'bg-green-500'
    if (percentage <= 90) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">Time planned</span>
        <span className="font-medium">
          {formatTime(plannedMinutes)} / {formatTime(targetMinutes)}
        </span>
      </div>

      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all', getColor())}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {percentage > 100 && (
        <p className="text-xs text-destructive">
          You may be overcommitting. Consider removing some tasks.
        </p>
      )}
    </div>
  )
}
