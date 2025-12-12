'use client'

import { useState } from 'react'

interface Action {
  id: string
  title: string
  description?: string
  estimated_minutes?: number
}

interface ActionEditFormProps {
  action: Action
  onSave: (updated: Partial<Action>) => void
  onCancel: () => void
}

export function ActionEditForm({
  action,
  onSave,
  onCancel
}: ActionEditFormProps) {
  const [title, setTitle] = useState(action.title)
  const [estimatedMinutes, setEstimatedMinutes] = useState(
    action.estimated_minutes ?? 15
  )
  const [description, setDescription] = useState(
    action.description ?? ''
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave({
      title: title.trim(),
      estimated_minutes: estimatedMinutes,
      description: description.trim() || undefined
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium">What needs to be done?</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full mt-1 rounded-md border p-2"
          autoFocus
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium">How long? (minutes)</label>
        <input
          type="number"
          value={estimatedMinutes}
          onChange={(e) => setEstimatedMinutes(parseInt(e.target.value) || 15)}
          min={5}
          max={480}
          step={5}
          className="w-full mt-1 rounded-md border p-2"
        />
      </div>

      <div>
        <label className="text-sm font-medium">Any notes? (optional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full mt-1 rounded-md border p-2"
          rows={2}
        />
      </div>

      <div className="flex gap-2 justify-end">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-muted-foreground"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          Save
        </button>
      </div>
    </form>
  )
}
