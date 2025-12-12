'use client'

import { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'

interface TimerProps {
  mode: 'elapsed' | 'countdown'
  startTime?: Date
  durationMinutes?: number
  onComplete?: () => void
  onThreshold?: (minutes: number) => void
  thresholdMinutes?: number
  className?: string
}

export function Timer({
  mode,
  startTime = new Date(),
  durationMinutes = 25,
  onComplete,
  onThreshold,
  thresholdMinutes = 25,
  className
}: TimerProps) {
  const [seconds, setSeconds] = useState(0)
  const thresholdFiredRef = useRef(false)

  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = Math.floor(
        (Date.now() - startTime.getTime()) / 1000
      )
      setSeconds(elapsed)

      const minutes = Math.floor(elapsed / 60)
      if (minutes >= thresholdMinutes && !thresholdFiredRef.current) {
        thresholdFiredRef.current = true
        onThreshold?.(minutes)
      }

      if (mode === 'countdown') {
        const remaining = durationMinutes * 60 - elapsed
        if (remaining <= 0) {
          onComplete?.()
          clearInterval(interval)
        }
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [startTime, durationMinutes, mode, thresholdMinutes, onThreshold, onComplete])

  const displaySeconds = mode === 'countdown'
    ? Math.max(0, durationMinutes * 60 - seconds)
    : seconds

  const minutes = Math.floor(displaySeconds / 60)
  const secs = displaySeconds % 60

  return (
    <div className={cn('font-mono text-2xl text-muted-foreground', className)}>
      {String(minutes).padStart(2, '0')}:{String(secs).padStart(2, '0')}
    </div>
  )
}
