import { type ReactNode } from 'react'

interface EmptyStateProps {
  title?: string
  message: string
  icon?: ReactNode
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({
  title,
  message,
  icon,
  action
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && (
        <div className="mb-4 text-muted-foreground">{icon}</div>
      )}
      {title && (
        <h3 className="font-medium text-lg mb-2">{title}</h3>
      )}
      <p className="text-muted-foreground max-w-sm">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

export function EmptyInbox() {
  return (
    <EmptyState
      title="Inbox is clear"
      message="Nothing waiting for your attention. Enjoy the calm."
    />
  )
}

export function EmptyToday() {
  return (
    <EmptyState
      title="No plan yet"
      message="Drag some tasks from inbox to start your day."
    />
  )
}
