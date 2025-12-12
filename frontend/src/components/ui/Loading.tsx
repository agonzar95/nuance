import { cn } from '@/lib/utils'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
}

export function Spinner({ size = 'md' }: SpinnerProps) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }
  return (
    <div
      className={cn('animate-spin rounded-full border-2 border-muted border-t-foreground', sizes[size])}
      role="status"
      aria-label="Loading"
    />
  )
}

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div className={cn('animate-pulse bg-muted rounded', className)} />
  )
}

export function ActionCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4">
      <Skeleton className="h-5 w-3/4 mb-2" />
      <Skeleton className="h-4 w-1/4" />
    </div>
  )
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <Spinner size="lg" />
    </div>
  )
}
