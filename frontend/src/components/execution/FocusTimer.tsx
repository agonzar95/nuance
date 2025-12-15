'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface FocusTimerProps {
  seconds: number
  className?: string
}

/**
 * Displays elapsed time in a subtle, non-pressuring format.
 * Format: MM:SS for times under 1 hour, H:MM:SS for longer sessions.
 */
export function FocusTimer({ seconds, className }: FocusTimerProps) {
  const formatTime = (totalSeconds: number): string => {
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const secs = totalSeconds % 60

    const pad = (n: number) => n.toString().padStart(2, '0')

    if (hours > 0) {
      return `${hours}:${pad(minutes)}:${pad(secs)}`
    }
    return `${pad(minutes)}:${pad(secs)}`
  }

  return (
    <div
      className={cn(
        'text-muted-foreground font-mono text-sm',
        className
      )}
    >
      {formatTime(seconds)}
    </div>
  )
}

interface UseFocusTimerOptions {
  initialSeconds?: number
  autoStart?: boolean
}

/**
 * Hook to manage focus timer state with pause/resume/reset controls.
 */
export function useFocusTimer(actionId: string, options: UseFocusTimerOptions = {}) {
  const { initialSeconds = 0, autoStart = true } = options
  const [seconds, setSeconds] = useState(initialSeconds)
  const [isRunning, setIsRunning] = useState(autoStart)

  // Reset timer when action changes
  useEffect(() => {
    setSeconds(initialSeconds)
    setIsRunning(autoStart)
  }, [actionId, initialSeconds, autoStart])

  useEffect(() => {
    if (!isRunning) return

    const interval = setInterval(() => {
      setSeconds(s => s + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [isRunning])

  const pause = () => setIsRunning(false)
  const resume = () => setIsRunning(true)
  const reset = () => setSeconds(0)

  return { seconds, pause, resume, reset, isRunning }
}
