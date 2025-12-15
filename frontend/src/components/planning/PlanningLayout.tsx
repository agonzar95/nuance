'use client'

/**
 * PLN-003: Drag to Plan (also enables PLN-004: Reorder Tasks)
 *
 * Main layout for the planning page that enables:
 * - Drag actions from inbox to today zone
 * - Drag from today back to inbox
 * - Reorder within today zone
 */

import { useCallback } from 'react'
import {
  DragDropContext,
  Droppable,
  Draggable,
  type DropResult,
  type DraggableProvided,
  type DroppableProvided,
  type DroppableStateSnapshot,
} from '@hello-pangea/dnd'
import { cn } from '@/lib/utils'
import { InboxView, type Suggestion } from './InboxView'
import { TodayView, TodayActionCard } from './TodayView'
import { TimeBudget } from './TimeBudget'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface PlanningLayoutProps {
  /** Inbox suggestions from AI */
  suggestions: Suggestion[]
  /** IDs of selected inbox items (for multi-select approach) */
  selectedIds: string[]
  /** Handler for selecting inbox item */
  onSelect: (actionId: string) => void
  /** Handler for deselecting inbox item */
  onDeselect: (actionId: string) => void
  /** Today's planned actions */
  todayActions: Action[]
  /** Handler for adding action to today */
  onAddToToday: (actionId: string) => void
  /** Handler for removing action from today */
  onRemoveFromToday: (actionId: string) => void
  /** Handler for reordering today's actions */
  onReorderToday: (actionIds: string[]) => void
  /** Handler for starting the day */
  onStartDay: () => void
  /** Whether inbox is loading */
  isInboxLoading?: boolean
  /** Whether day commit is in progress */
  isStarting?: boolean
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function PlanningLayout({
  suggestions,
  selectedIds,
  onSelect,
  onDeselect,
  todayActions,
  onAddToToday,
  onRemoveFromToday,
  onReorderToday,
  onStartDay,
  isInboxLoading,
  isStarting,
  className,
}: PlanningLayoutProps) {
  // Calculate total minutes for today
  const totalMinutes = todayActions.reduce(
    (sum, action) => sum + (action.estimated_minutes || 0),
    0
  )

  // Handle drag end event
  const handleDragEnd = useCallback(
    (result: DropResult) => {
      const { source, destination, draggableId } = result

      // Dropped outside a droppable
      if (!destination) return

      // Drag from inbox to today
      if (
        source.droppableId === 'planning-inbox' &&
        destination.droppableId === 'planning-today'
      ) {
        onAddToToday(draggableId)
        return
      }

      // Drag from today back to inbox (remove from today)
      if (
        source.droppableId === 'planning-today' &&
        destination.droppableId === 'planning-inbox'
      ) {
        onRemoveFromToday(draggableId)
        return
      }

      // Reorder within today (PLN-004)
      if (
        source.droppableId === 'planning-today' &&
        destination.droppableId === 'planning-today' &&
        source.index !== destination.index
      ) {
        const newOrder = Array.from(todayActions.map((a) => a.id))
        const [removed] = newOrder.splice(source.index, 1)
        newOrder.splice(destination.index, 0, removed)
        onReorderToday(newOrder)
      }
    },
    [todayActions, onAddToToday, onRemoveFromToday, onReorderToday]
  )

  // Filter out actions already in today from inbox suggestions
  const todayActionIds = new Set(todayActions.map((a) => a.id))
  const availableSuggestions = suggestions.filter(
    (s) => !todayActionIds.has(s.action.id)
  )

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className={cn('flex flex-col h-full', className)}>
        {/* Time budget indicator */}
        <div className="mb-4">
          <TimeBudget plannedMinutes={totalMinutes} />
        </div>

        {/* Two-column layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1 min-h-0">
          {/* Inbox Column */}
          <DroppableInboxColumn
            suggestions={availableSuggestions}
            selectedIds={selectedIds}
            onSelect={onSelect}
            onDeselect={onDeselect}
            isLoading={isInboxLoading}
          />

          {/* Today Column */}
          <DroppableTodayColumn
            actions={todayActions}
            totalMinutes={totalMinutes}
            onRemove={onRemoveFromToday}
            onStartDay={onStartDay}
            isStarting={isStarting}
          />
        </div>
      </div>
    </DragDropContext>
  )
}

// ============================================================================
// Inbox Droppable Column
// ============================================================================

interface DroppableInboxColumnProps {
  suggestions: Suggestion[]
  selectedIds: string[]
  onSelect: (actionId: string) => void
  onDeselect: (actionId: string) => void
  isLoading?: boolean
}

function DroppableInboxColumn({
  suggestions,
  selectedIds,
  onSelect,
  onDeselect,
  isLoading,
}: DroppableInboxColumnProps) {
  return (
    <Droppable droppableId="planning-inbox">
      {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.droppableProps}
          className={cn(
            'flex flex-col rounded-lg border-2 border-dashed p-4 min-h-[300px] overflow-y-auto',
            snapshot.isDraggingOver
              ? 'border-primary bg-primary/5'
              : 'border-muted-foreground/20'
          )}
        >
          <h3 className="font-medium text-lg mb-4">
            Inbox
            <span className="text-muted-foreground text-sm ml-2">
              ({suggestions.length})
            </span>
          </h3>

          {isLoading ? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              Loading suggestions...
            </div>
          ) : suggestions.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
              {selectedIds.length > 0
                ? 'All selected items are in today'
                : 'No suggestions available'}
            </div>
          ) : (
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <DraggableInboxCard
                  key={suggestion.action.id}
                  suggestion={suggestion}
                  index={index}
                  isSelected={selectedIds.includes(suggestion.action.id)}
                  onToggle={() =>
                    selectedIds.includes(suggestion.action.id)
                      ? onDeselect(suggestion.action.id)
                      : onSelect(suggestion.action.id)
                  }
                />
              ))}
            </div>
          )}
          {provided.placeholder}
        </div>
      )}
    </Droppable>
  )
}

// ============================================================================
// Today Droppable Column
// ============================================================================

interface DroppableTodayColumnProps {
  actions: Action[]
  totalMinutes: number
  onRemove: (actionId: string) => void
  onStartDay: () => void
  isStarting?: boolean
}

function DroppableTodayColumn({
  actions,
  totalMinutes,
  onRemove,
  onStartDay,
  isStarting,
}: DroppableTodayColumnProps) {
  return (
    <Droppable droppableId="planning-today">
      {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.droppableProps}
          className={cn(
            'flex flex-col rounded-lg border-2 border-dashed p-4 min-h-[300px]',
            snapshot.isDraggingOver
              ? 'border-primary bg-primary/5'
              : 'border-muted-foreground/20'
          )}
        >
          <TodayView
            actions={actions}
            totalMinutes={totalMinutes}
            onReorder={() => {}} // Handled by DragDropContext
            onStartDay={onStartDay}
            onRemove={onRemove}
            canStart={actions.length > 0}
            isStarting={isStarting}
          />

          {/* Render draggable cards for today */}
          {actions.length === 0 && !snapshot.isDraggingOver && (
            <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
              Drag tasks here to plan your day
            </div>
          )}

          {provided.placeholder}
        </div>
      )}
    </Droppable>
  )
}

// ============================================================================
// Draggable Inbox Card
// ============================================================================

interface DraggableInboxCardProps {
  suggestion: Suggestion
  index: number
  isSelected: boolean
  onToggle: () => void
}

function DraggableInboxCard({
  suggestion,
  index,
  isSelected,
  onToggle,
}: DraggableInboxCardProps) {
  const { action, reasoning } = suggestion

  return (
    <Draggable draggableId={action.id} index={index}>
      {(provided: DraggableProvided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={cn(
            'rounded-lg border bg-card p-3 cursor-grab active:cursor-grabbing transition-all',
            snapshot.isDragging && 'shadow-lg ring-2 ring-primary',
            isSelected && 'ring-2 ring-primary/50 bg-primary/5'
          )}
          onClick={onToggle}
        >
          <h4 className="font-medium text-sm truncate">{action.title}</h4>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
            {reasoning}
          </p>
        </div>
      )}
    </Draggable>
  )
}
