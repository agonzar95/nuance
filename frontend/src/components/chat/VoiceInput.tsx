'use client'

/**
 * CAP-003: Chat Voice Input
 *
 * Voice recording button with transcription support.
 * Records audio via MediaRecorder, sends to transcription API,
 * and passes transcribed text to parent component.
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'

// Error types for voice recording
export type VoiceErrorType = 'permission' | 'transcription' | 'network' | 'unsupported' | null

export interface VoiceErrorState {
  hasError: boolean
  errorType: VoiceErrorType
  message: string
}

interface VoiceInputProps {
  onTranscription: (text: string) => void
  disabled?: boolean
  onError?: (error: VoiceErrorState) => void
  onRecordingChange?: (isRecording: boolean) => void
}

const ERROR_MESSAGES: Record<NonNullable<VoiceErrorType>, string> = {
  permission: 'Microphone access denied. Please enable in browser settings.',
  transcription: "Couldn't understand that. Try speaking more clearly.",
  network: 'Connection issue. Check your internet and try again.',
  unsupported: 'Voice recording is not supported in this browser.',
}

export function VoiceInput({
  onTranscription,
  disabled,
  onError,
  onRecordingChange,
}: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [duration, setDuration] = useState(0)
  const [error, setError] = useState<VoiceErrorState>({
    hasError: false,
    errorType: null,
    message: '',
  })

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  // Check browser support
  const isSupported = typeof navigator !== 'undefined' && navigator.mediaDevices?.getUserMedia

  const handleError = useCallback(
    (type: NonNullable<VoiceErrorType>, err?: Error) => {
      const errorState: VoiceErrorState = {
        hasError: true,
        errorType: type,
        message: ERROR_MESSAGES[type],
      }
      setError(errorState)
      onError?.(errorState)
      console.error('Voice error:', type, err)
    },
    [onError]
  )

  const clearError = useCallback(() => {
    setError({ hasError: false, errorType: null, message: '' })
  }, [])

  const startRecording = useCallback(async () => {
    if (!isSupported) {
      handleError('unsupported')
      return
    }

    clearError()

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/mp4',
      })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorder.mimeType || 'audio/webm'
        const blob = new Blob(chunksRef.current, { type: mimeType })

        // Clean up stream
        streamRef.current?.getTracks().forEach((t) => t.stop())
        streamRef.current = null

        await transcribe(blob)
      }

      mediaRecorder.onerror = () => {
        handleError('network')
        setIsRecording(false)
        onRecordingChange?.(false)
      }

      mediaRecorder.start()
      setIsRecording(true)
      setDuration(0)
      onRecordingChange?.(true)
    } catch (err) {
      if (err instanceof Error && err.name === 'NotAllowedError') {
        handleError('permission', err)
      } else {
        handleError('network', err instanceof Error ? err : undefined)
      }
    }
  }, [isSupported, handleError, clearError, onRecordingChange])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      onRecordingChange?.(false)
    }
  }, [onRecordingChange])

  const transcribe = async (blob: Blob) => {
    setIsTranscribing(true)
    try {
      const response = await api.transcription.transcribe(blob)
      if (response.text.trim()) {
        onTranscription(response.text.trim())
      }
    } catch (err) {
      console.error('Transcription error:', err)
      handleError('transcription', err instanceof Error ? err : undefined)
    } finally {
      setIsTranscribing(false)
    }
  }

  // Duration timer
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setDuration((d) => d + 1)
      }, 1000)
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [isRecording])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop())
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const handleClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const handleRetry = () => {
    clearError()
    startRecording()
  }

  // Format duration as M:SS
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const isDisabled = disabled || isTranscribing || !isSupported

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleClick}
        disabled={isDisabled}
        className={cn(
          'p-3 rounded-full transition-all',
          isRecording
            ? 'bg-red-500 text-white animate-pulse'
            : 'bg-muted hover:bg-muted/80',
          isDisabled && 'opacity-50 cursor-not-allowed',
          isTranscribing && 'animate-spin'
        )}
        aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
      >
        {isTranscribing ? (
          <SpinnerIcon className="w-5 h-5" />
        ) : (
          <MicIcon className={cn('w-5 h-5', isRecording && 'text-white')} />
        )}
      </button>

      {/* Recording duration indicator */}
      {isRecording && (
        <span className="absolute -top-2 -right-2 text-xs bg-red-500 text-white px-1.5 py-0.5 rounded-full min-w-[2rem] text-center">
          {formatDuration(duration)}
        </span>
      )}

      {/* Error display */}
      {error.hasError && (
        <div className="absolute bottom-full mb-2 left-0 right-0 w-64 -translate-x-1/2 translate-x-[calc(50%-1.25rem)]">
          <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-sm">
            <AlertCircleIcon className="w-4 h-4 text-destructive flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="text-destructive">{error.message}</span>
              {error.errorType !== 'permission' && error.errorType !== 'unsupported' && (
                <button
                  onClick={handleRetry}
                  className="block mt-1 text-primary hover:underline"
                >
                  Try again
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Icon components
function MicIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  )
}

function SpinnerIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  )
}

function AlertCircleIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" x2="12" y1="8" y2="12" />
      <line x1="12" x2="12.01" y1="16" y2="16" />
    </svg>
  )
}
