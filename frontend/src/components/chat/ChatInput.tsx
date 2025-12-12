'use client'

import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSend: (content: string) => void
  disabled?: boolean
  placeholder?: string
  maxLength?: number
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "What's on your mind?",
  maxLength = 2000
}: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSend = () => {
    const trimmed = value.trim()
    if (trimmed && !disabled) {
      onSend(trimmed)
      setValue('')
      textareaRef.current?.focus()
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [value])

  return (
    <div className="border-t p-4 bg-background">
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, maxLength))}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            'flex-1 resize-none rounded-lg border p-3',
            'focus:outline-none focus:ring-2 focus:ring-primary',
            'max-h-32 overflow-y-auto',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className={cn(
            'p-3 rounded-lg bg-primary text-primary-foreground',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
          aria-label="Send message"
        >
          <SendIcon className="w-5 h-5" />
        </button>
      </div>
      {value.length > maxLength * 0.9 && (
        <p className="text-xs text-muted-foreground mt-1">
          {value.length}/{maxLength}
        </p>
      )}
    </div>
  )
}

function SendIcon({ className }: { className?: string }) {
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
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  )
}
