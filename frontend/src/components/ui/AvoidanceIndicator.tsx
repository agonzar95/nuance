import { cn } from '@/lib/utils'

interface AvoidanceIndicatorProps {
  weight: number // 1-5
  size?: 'sm' | 'md' | 'lg'
}

export function AvoidanceIndicator({
  weight,
  size = 'sm'
}: AvoidanceIndicatorProps) {
  const clampedWeight = Math.min(5, Math.max(1, weight))

  const sizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5'
  }

  return (
    <div
      className="flex gap-0.5"
      role="img"
      aria-label={`Avoidance weight: ${clampedWeight} of 5`}
    >
      {Array.from({ length: 5 }).map((_, i) => (
        <span
          key={i}
          className={cn(
            'rounded-full',
            sizeClasses[size],
            i < clampedWeight
              ? 'bg-foreground/60'
              : 'bg-muted-foreground/20'
          )}
        />
      ))}
    </div>
  )
}
