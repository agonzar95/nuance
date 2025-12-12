# Planning Feature Specifications

**Category:** PLN (Frontend Planning)
**Total Features:** 9
**Complexity:** 4 Easy, 5 Medium, 0 Hard

---

## PLN-001: Inbox View

### A. User Story

> As a **User**, I want to **see AI-curated candidate actions for today** so that I can choose what to focus on without being overwhelmed.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Display up to 12 candidate actions prioritized by AI. Show each action with avoidance weight, estimate, and reasoning. Support selecting actions for today's plan. |
| **2** | **Logic Flow** | 1. Fetch AI-generated suggestions on mount.<br>2. Display max 12 candidates in scrollable list.<br>3. Show reasoning for each suggestion.<br>4. Allow drag to Today zone or tap to add.<br>5. Track selected actions. |
| **3** | **Formal Interfaces** | **InboxView Component (components/planning/InboxView.tsx):**<br>```typescript<br>interface Suggestion {<br>  action: Action<br>  reasoning: string<br>  priorityScore: number<br>}<br><br>interface InboxViewProps {<br>  suggestions: Suggestion[]<br>  selectedIds: string[]<br>  onSelect: (actionId: string) => void<br>  onDeselect: (actionId: string) => void<br>  isLoading?: boolean<br>}<br><br>export function InboxView({<br>  suggestions,<br>  selectedIds,<br>  onSelect,<br>  onDeselect,<br>  isLoading<br>}: InboxViewProps) {<br>  if (isLoading) {<br>    return (<br>      <div className="space-y-3"><br>        {Array.from({ length: 5 }).map((_, i) => (<br>          <ActionCardSkeleton key={i} /><br>        ))}<br>      </div><br>    )<br>  }<br>  <br>  if (suggestions.length === 0) {<br>    return <EmptyInbox /><br>  }<br>  <br>  return (<br>    <div className="space-y-4"><br>      <h2 className="font-medium text-lg"><br>        Today's Candidates<br>        <span className="text-muted-foreground text-sm ml-2"><br>          ({suggestions.length})<br>        </span><br>      </h2><br>      <br>      <div className="space-y-3"><br>        {suggestions.slice(0, 12).map(({ action, reasoning }) => {<br>          const isSelected = selectedIds.includes(action.id)<br>          <br>          return (<br>            <InboxCard<br>              key={action.id}<br>              action={action}<br>              reasoning={reasoning}<br>              isSelected={isSelected}<br>              onToggle={() => <br>                isSelected ? onDeselect(action.id) : onSelect(action.id)<br>              }<br>            /><br>          )<br>        })}<br>      </div><br>    </div><br>  )<br>}<br>```<br><br>**InboxCard Component:**<br>```typescript<br>interface InboxCardProps {<br>  action: Action<br>  reasoning: string<br>  isSelected: boolean<br>  onToggle: () => void<br>}<br><br>function InboxCard({ action, reasoning, isSelected, onToggle }: InboxCardProps) {<br>  return (<br>    <div<br>      className={cn(<br>        'rounded-lg border p-4 cursor-pointer transition-all',<br>        isSelected && 'ring-2 ring-primary bg-primary/5'<br>      )}<br>      onClick={onToggle}<br>    ><br>      <div className="flex items-start justify-between"><br>        <div className="flex-1"><br>          <h3 className="font-medium">{action.title}</h3><br>          <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground"><br>            <AvoidanceIndicator weight={action.avoidance_weight} /><br>            {action.estimated_minutes && (<br>              <span>~{action.estimated_minutes}min</span><br>            )}<br>          </div><br>        </div><br>        <div className={cn(<br>          'w-6 h-6 rounded-full border-2 flex items-center justify-center',<br>          isSelected ? 'bg-primary border-primary' : 'border-muted-foreground'<br>        )}><br>          {isSelected && <Check className="w-4 h-4 text-white" />}<br>        </div><br>      </div><br>      <br>      <p className="text-sm text-muted-foreground mt-2 italic"><br>        "{reasoning}"<br>      </p><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open inbox. See suggested actions with AI reasoning. Tap action. See checkmark. Tap again. Deselected. |
| **2** | **Test Logic** | **Given** 5 suggestions,<br>**When** rendered,<br>**Then** 5 InboxCards visible.<br>**When** card clicked,<br>**Then** onSelect called with action ID. |
| **3** | **Formal Tests** | Render with mock suggestions. Click card. Verify onSelect called. Click selected card. Verify onDeselect called. |

### D. Atomicity Validation

- **Yes.** Inbox display and selection only.

### E. Dependencies

- FE-006 (ActionCard component).
- FE-007 (Avoidance indicator).
- FE-010 (Empty state).

---

## PLN-002: Today View

### A. User Story

> As a **User**, I want to **see my committed plan for today** so that I know what I've decided to work on.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Display today's committed actions in order. Show time slots/estimates. Support reordering. Include "Start Day" button when ready. |
| **2** | **Logic Flow** | 1. Fetch today's snapshot with actions.<br>2. Display actions in committed order.<br>3. Show cumulative time estimate.<br>4. Enable drag-to-reorder.<br>5. Show Start Day button. |
| **3** | **Formal Interfaces** | **TodayView Component (components/planning/TodayView.tsx):**<br>```typescript<br>interface TodayViewProps {<br>  actions: Action[]<br>  totalMinutes: number<br>  onReorder: (actionIds: string[]) => void<br>  onStartDay: () => void<br>  onRemove: (actionId: string) => void<br>  canStart: boolean<br>}<br><br>export function TodayView({<br>  actions,<br>  totalMinutes,<br>  onReorder,<br>  onStartDay,<br>  onRemove,<br>  canStart<br>}: TodayViewProps) {<br>  if (actions.length === 0) {<br>    return <EmptyToday /><br>  }<br>  <br>  const formatTime = (minutes: number) => {<br>    const hours = Math.floor(minutes / 60)<br>    const mins = minutes % 60<br>    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`<br>  }<br>  <br>  return (<br>    <div className="flex flex-col h-full"><br>      <div className="flex items-center justify-between mb-4"><br>        <h2 className="font-medium text-lg"><br>          Today — {format(new Date(), 'EEEE, MMMM d')}<br>        </h2><br>        <span className="text-muted-foreground"><br>          {formatTime(totalMinutes)} planned<br>        </span><br>      </div><br>      <br>      <DragDropContext onDragEnd={handleDragEnd}><br>        <Droppable droppableId="today-list"><br>          {(provided) => (<br>            <div<br>              {...provided.droppableProps}<br>              ref={provided.innerRef}<br>              className="flex-1 space-y-2 overflow-y-auto"<br>            ><br>              {actions.map((action, index) => (<br>                <Draggable<br>                  key={action.id}<br>                  draggableId={action.id}<br>                  index={index}<br>                ><br>                  {(provided, snapshot) => (<br>                    <div<br>                      ref={provided.innerRef}<br>                      {...provided.draggableProps}<br>                    ><br>                      <TodayActionCard<br>                        action={action}<br>                        dragHandleProps={provided.dragHandleProps}<br>                        isDragging={snapshot.isDragging}<br>                        onRemove={() => onRemove(action.id)}<br>                      /><br>                    </div><br>                  )}<br>                </Draggable><br>              ))}<br>              {provided.placeholder}<br>            </div><br>          )}<br>        </Droppable><br>      </DragDropContext><br>      <br>      <div className="mt-4 pt-4 border-t"><br>        <button<br>          onClick={onStartDay}<br>          disabled={!canStart}<br>          className={cn(<br>            'w-full py-3 rounded-lg font-medium',<br>            'bg-primary text-primary-foreground',<br>            'disabled:opacity-50 disabled:cursor-not-allowed'<br>          )}<br>        ><br>          Start Day<br>        </button><br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | View today with 3 actions. See total time. Drag to reorder. Click Start Day. Enters focus mode. |
| **2** | **Test Logic** | **Given** 3 actions totaling 90 minutes,<br>**Then** "1h 30m planned" displayed.<br>**When** drag action 3 to position 1,<br>**Then** onReorder called with new order. |
| **3** | **Formal Tests** | Render with actions. Verify time display. Simulate drag. Verify reorder callback. Click start. Verify onStartDay. |

### D. Atomicity Validation

- **Yes.** Today view display only.

### E. Dependencies

- PLN-004 (Reorder functionality).
- PLN-005 (Day commit flow).
- FE-010 (Empty state).

---

## PLN-003: Drag to Plan

### A. User Story

> As a **User**, I want to **drag actions from inbox to today** so that I can visually build my plan.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Enable drag-and-drop from inbox zone to today zone. Visual feedback during drag. Action moves from inbox to today on successful drop. |
| **2** | **Logic Flow** | 1. User grabs action card in inbox.<br>2. Card lifts with shadow, origin dims.<br>3. Today zone highlights as drop target.<br>4. On drop in Today, action added to plan.<br>5. Card removed from inbox view. |
| **3** | **Formal Interfaces** | **PlanningLayout Component (components/planning/PlanningLayout.tsx):**<br>```typescript<br>interface PlanningLayoutProps {<br>  suggestions: Suggestion[]<br>  todayActions: Action[]<br>  onAddToToday: (actionId: string) => void<br>  onRemoveFromToday: (actionId: string) => void<br>  onReorderToday: (actionIds: string[]) => void<br>}<br><br>export function PlanningLayout({<br>  suggestions,<br>  todayActions,<br>  onAddToToday,<br>  onRemoveFromToday,<br>  onReorderToday<br>}: PlanningLayoutProps) {<br>  const handleDragEnd = (result: DropResult) => {<br>    const { source, destination, draggableId } = result<br>    <br>    if (!destination) return<br>    <br>    // Drag from inbox to today<br>    if (<br>      source.droppableId === 'inbox' &&<br>      destination.droppableId === 'today'<br>    ) {<br>      onAddToToday(draggableId)<br>      return<br>    }<br>    <br>    // Drag from today back to inbox<br>    if (<br>      source.droppableId === 'today' &&<br>      destination.droppableId === 'inbox'<br>    ) {<br>      onRemoveFromToday(draggableId)<br>      return<br>    }<br>    <br>    // Reorder within today<br>    if (<br>      source.droppableId === 'today' &&<br>      destination.droppableId === 'today'<br>    ) {<br>      const newOrder = Array.from(todayActions.map(a => a.id))<br>      const [removed] = newOrder.splice(source.index, 1)<br>      newOrder.splice(destination.index, 0, removed)<br>      onReorderToday(newOrder)<br>    }<br>  }<br>  <br>  return (<br>    <DragDropContext onDragEnd={handleDragEnd}><br>      <div className="grid grid-cols-2 gap-6 h-full"><br>        {/* Inbox Column */}<br>        <Droppable droppableId="inbox"><br>          {(provided, snapshot) => (<br>            <div<br>              ref={provided.innerRef}<br>              {...provided.droppableProps}<br>              className={cn(<br>                'rounded-lg border-2 border-dashed p-4',<br>                snapshot.isDraggingOver && 'border-primary bg-primary/5'<br>              )}<br>            ><br>              <h3 className="font-medium mb-4">Inbox</h3><br>              {/* Draggable inbox items */}<br>              {provided.placeholder}<br>            </div><br>          )}<br>        </Droppable><br>        <br>        {/* Today Column */}<br>        <Droppable droppableId="today"><br>          {(provided, snapshot) => (<br>            <div<br>              ref={provided.innerRef}<br>              {...provided.droppableProps}<br>              className={cn(<br>                'rounded-lg border-2 border-dashed p-4',<br>                snapshot.isDraggingOver && 'border-primary bg-primary/5'<br>              )}<br>            ><br>              <h3 className="font-medium mb-4">Today</h3><br>              {/* Draggable today items */}<br>              {provided.placeholder}<br>            </div><br>          )}<br>        </Droppable><br>      </div><br>    </DragDropContext><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Grab inbox card. Drag to Today zone. Zone highlights. Drop. Action appears in Today. Removed from inbox. |
| **2** | **Test Logic** | **Given** action in inbox,<br>**When** dragged to today droppable,<br>**Then** onAddToToday called with action ID. |
| **3** | **Formal Tests** | Render layout. Simulate drag from inbox to today. Verify callback. Verify visual feedback classes applied during drag. |

### D. Atomicity Validation

- **Yes.** Drag-and-drop between zones only.

### E. Dependencies

- PLN-001 (Inbox view).
- PLN-002 (Today view).

---

## PLN-004: Reorder Tasks

### A. User Story

> As a **User**, I want to **reorder my day's tasks** so that I can adjust the sequence based on energy and priorities.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Enable drag handles on today's task cards. Drag up/down to reorder. Other tasks shift smoothly. Save new order. |
| **2** | **Logic Flow** | 1. User grabs drag handle.<br>2. Card lifts, others make space.<br>3. Drag up/down changes position.<br>4. On release, order is saved.<br>5. API call persists new order. |
| **3** | **Formal Interfaces** | **TodayActionCard with Drag Handle:**<br>```typescript<br>interface TodayActionCardProps {<br>  action: Action<br>  dragHandleProps?: DraggableProvidedDragHandleProps<br>  isDragging?: boolean<br>  onRemove: () => void<br>}<br><br>function TodayActionCard({<br>  action,<br>  dragHandleProps,<br>  isDragging,<br>  onRemove<br>}: TodayActionCardProps) {<br>  return (<br>    <div<br>      className={cn(<br>        'flex items-center gap-3 rounded-lg border bg-card p-3',<br>        isDragging && 'shadow-lg ring-2 ring-primary'<br>      )}<br>    ><br>      {/* Drag Handle */}<br>      <div<br>        {...dragHandleProps}<br>        className="cursor-grab active:cursor-grabbing p-1"<br>      ><br>        <GripVertical className="w-5 h-5 text-muted-foreground" /><br>      </div><br>      <br>      {/* Action Content */}<br>      <div className="flex-1 min-w-0"><br>        <h4 className="font-medium truncate">{action.title}</h4><br>        <div className="flex items-center gap-2 text-sm text-muted-foreground"><br>          <AvoidanceIndicator weight={action.avoidance_weight} /><br>          {action.estimated_minutes && (<br>            <span>~{action.estimated_minutes}min</span><br>          )}<br>        </div><br>      </div><br>      <br>      {/* Remove Button */}<br>      <button<br>        onClick={onRemove}<br>        className="p-2 text-muted-foreground hover:text-destructive"<br>        aria-label="Remove from today"<br>      ><br>        <X className="w-4 h-4" /><br>      </button><br>    </div><br>  )<br>}<br>```<br><br>**Reorder Handler:**<br>```typescript<br>const handleReorder = async (newOrder: string[]) => {<br>  // Optimistic update<br>  setTodayActions(prev => {<br>    const actionMap = new Map(prev.map(a => [a.id, a]))<br>    return newOrder.map(id => actionMap.get(id)!)<br>  })<br>  <br>  // Persist to server<br>  try {<br>    await api.planning.updateTodayOrder(newOrder)<br>  } catch (err) {<br>    toast.error('Failed to save order')<br>    // Revert on error<br>    refetchToday()<br>  }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Grab drag handle. Drag task up. Other tasks shift down. Release. New order saved. |
| **2** | **Test Logic** | **Given** tasks [A, B, C],<br>**When** C dragged to position 0,<br>**Then** order becomes [C, A, B].<br>**Then** API called with new order. |
| **3** | **Formal Tests** | Render tasks. Simulate drag reorder. Verify state update. Verify API call with correct order. |

### D. Atomicity Validation

- **Yes.** Reorder functionality only.

### E. Dependencies

- PLN-002 (Today view).
- FE-002 (Optimistic updates).

---

## PLN-005: Day Commit

### A. User Story

> As a **User**, I want to **commit to my day's plan** so that I can enter focus mode with a clear agenda.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Start Day" button commits the plan. Creates daily snapshot. Transitions to focus mode with first task. Shows brief confirmation. |
| **2** | **Logic Flow** | 1. User clicks "Start Day".<br>2. Validate at least one action selected.<br>3. Create daily snapshot in database.<br>4. Mark actions as today's plan.<br>5. Navigate to focus mode with first action. |
| **3** | **Formal Interfaces** | **Day Commit Hook (hooks/useDayCommit.ts):**<br>```typescript<br>interface DayCommitResult {<br>  commitDay: () => Promise<void><br>  isCommitting: boolean<br>  canCommit: boolean<br>}<br><br>export function useDayCommit(actionIds: string[]): DayCommitResult {<br>  const router = useRouter()<br>  const [isCommitting, setIsCommitting] = useState(false)<br>  <br>  const canCommit = actionIds.length > 0<br>  <br>  const commitDay = async () => {<br>    if (!canCommit) return<br>    <br>    setIsCommitting(true)<br>    try {<br>      const { dailySnapshot, actions } = await api.planning.commitDay(<br>        actionIds<br>      )<br>      <br>      // Navigate to focus mode with first action<br>      router.push(`/focus/${actions[0].id}`)<br>    } catch (err) {<br>      toast.error('Failed to start day')<br>    } finally {<br>      setIsCommitting(false)<br>    }<br>  }<br>  <br>  return { commitDay, isCommitting, canCommit }<br>}<br>```<br><br>**Start Day Button:**<br>```typescript<br>function StartDayButton({ actionIds }: { actionIds: string[] }) {<br>  const { commitDay, isCommitting, canCommit } = useDayCommit(actionIds)<br>  <br>  return (<br>    <button<br>      onClick={commitDay}<br>      disabled={!canCommit \|\| isCommitting}<br>      className={cn(<br>        'w-full py-4 rounded-lg font-medium text-lg',<br>        'bg-primary text-primary-foreground',<br>        'disabled:opacity-50',<br>        'transition-all hover:bg-primary/90'<br>      )}<br>    ><br>      {isCommitting ? (<br>        <span className="flex items-center justify-center gap-2"><br>          <Spinner size="sm" /><br>          Starting...<br>        </span><br>      ) : (<br>        'Start Day'<br>      )}<br>    </button><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Select 3 actions. Click Start Day. Spinner shows. Navigates to focus mode with first action. |
| **2** | **Test Logic** | **Given** 3 action IDs selected,<br>**When** commitDay called,<br>**Then** API called with action IDs.<br>**Then** navigates to /focus/{firstActionId}. |
| **3** | **Formal Tests** | Mock API and router. Call commitDay. Verify API called. Verify navigation. |

### D. Atomicity Validation

- **Yes.** Day commit flow only.

### E. Dependencies

- PLN-002 (Today view).
- EXE-001 (Focus mode container).

---

## PLN-006: Time Budget Display

### A. User Story

> As a **User**, I want to **see how much time I've planned** so that I don't overcommit.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Display total planned time for today. Show visual indicator (bar or arc). Update as actions added/removed. Optional: show available time based on preferences. |
| **2** | **Logic Flow** | 1. Sum estimated_minutes for today's actions.<br>2. Calculate percentage of target (e.g., 8 hours).<br>3. Display as progress bar or text.<br>4. Color code: green (under), yellow (near), red (over). |
| **3** | **Formal Interfaces** | **TimeBudget Component (components/planning/TimeBudget.tsx):**<br>```typescript<br>interface TimeBudgetProps {<br>  plannedMinutes: number<br>  targetMinutes?: number // Default 480 (8 hours)<br>}<br><br>export function TimeBudget({<br>  plannedMinutes,<br>  targetMinutes = 480<br>}: TimeBudgetProps) {<br>  const percentage = Math.min(100, (plannedMinutes / targetMinutes) * 100)<br>  <br>  const formatTime = (minutes: number) => {<br>    const hours = Math.floor(minutes / 60)<br>    const mins = minutes % 60<br>    if (hours === 0) return `${mins}m`<br>    if (mins === 0) return `${hours}h`<br>    return `${hours}h ${mins}m`<br>  }<br>  <br>  const getColor = () => {<br>    if (percentage <= 70) return 'bg-green-500'<br>    if (percentage <= 90) return 'bg-yellow-500'<br>    return 'bg-red-500'<br>  }<br>  <br>  return (<br>    <div className="space-y-2"><br>      <div className="flex justify-between text-sm"><br>        <span className="text-muted-foreground">Time planned</span><br>        <span className="font-medium"><br>          {formatTime(plannedMinutes)} / {formatTime(targetMinutes)}<br>        </span><br>      </div><br>      <br>      <div className="h-2 rounded-full bg-muted overflow-hidden"><br>        <div<br>          className={cn('h-full rounded-full transition-all', getColor())}<br>          style={{ width: `${percentage}%` }}<br>        /><br>      </div><br>      <br>      {percentage > 100 && (<br>        <p className="text-xs text-destructive"><br>          You may be overcommitting. Consider removing some tasks.<br>        </p><br>      )}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Add 3 actions totaling 2 hours. See "2h / 8h" with green bar at 25%. Add more. Bar grows and changes color. |
| **2** | **Test Logic** | **Given** 240 minutes planned (4h),<br>**Then** shows "4h / 8h".<br>**Then** bar is 50% width.<br>**Then** color is green. |
| **3** | **Formal Tests** | Render with various minutes. Verify text. Verify bar width. Verify color thresholds. |

### D. Atomicity Validation

- **Yes.** Time display only.

### E. Dependencies

- None.

---

## PLN-007: Add More Tasks

### A. User Story

> As a **User**, I want to **add more tasks to today** from the planning view so that I can include things not in the AI suggestions.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Button to add new task opens quick capture. Captured task added directly to today's plan. Can also browse all actions to add. |
| **2** | **Logic Flow** | 1. Click "Add more" button.<br>2. Option A: Quick capture opens (mini chat).<br>3. Option B: Action picker shows all actions.<br>4. Selected/created action added to today.<br>5. Return to planning view. |
| **3** | **Formal Interfaces** | **AddTaskButton Component (components/planning/AddTaskButton.tsx):**<br>```typescript<br>interface AddTaskButtonProps {<br>  onAddAction: (action: Action) => void<br>}<br><br>export function AddTaskButton({ onAddAction }: AddTaskButtonProps) {<br>  const [isOpen, setIsOpen] = useState(false)<br>  const [mode, setMode] = useState<'capture' \| 'browse' \| null>(null)<br>  <br>  return (<br>    <><br>      <button<br>        onClick={() => setIsOpen(true)}<br>        className="w-full py-3 border-2 border-dashed rounded-lg text-muted-foreground hover:border-primary hover:text-primary transition-colors"<br>      ><br>        <Plus className="w-5 h-5 inline mr-2" /><br>        Add more tasks<br>      </button><br>      <br>      <Dialog open={isOpen} onOpenChange={setIsOpen}><br>        <DialogContent><br>          {!mode && (<br>            <div className="space-y-4"><br>              <h3 className="font-medium">Add a task</h3><br>              <button<br>                onClick={() => setMode('capture')}<br>                className="w-full p-4 text-left border rounded-lg hover:bg-muted"<br>              ><br>                <span className="font-medium">Quick capture</span><br>                <p className="text-sm text-muted-foreground"><br>                  Describe what you need to do<br>                </p><br>              </button><br>              <button<br>                onClick={() => setMode('browse')}<br>                className="w-full p-4 text-left border rounded-lg hover:bg-muted"<br>              ><br>                <span className="font-medium">Browse existing</span><br>                <p className="text-sm text-muted-foreground"><br>                  Add from your task list<br>                </p><br>              </button><br>            </div><br>          )}<br>          <br>          {mode === 'capture' && (<br>            <QuickCaptureForm<br>              onCapture={async (text) => {<br>                const action = await api.actions.quickCreate(text)<br>                onAddAction(action)<br>                setIsOpen(false)<br>                setMode(null)<br>              }}<br>            /><br>          )}<br>          <br>          {mode === 'browse' && (<br>            <ActionPicker<br>              onSelect={(action) => {<br>                onAddAction(action)<br>                setIsOpen(false)<br>                setMode(null)<br>              }}<br>            /><br>          )}<br>        </DialogContent><br>      </Dialog><br>    </><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Click "Add more". Choose "Quick capture". Type task. Submit. Task added to today's plan. |
| **2** | **Test Logic** | **Given** dialog open,<br>**When** "Quick capture" chosen,<br>**Then** capture form shown.<br>**When** submitted,<br>**Then** onAddAction called with new action. |
| **3** | **Formal Tests** | Open dialog. Click capture option. Submit form. Verify callback with action. Verify dialog closes. |

### D. Atomicity Validation

- **Yes.** Add task flow only.

### E. Dependencies

- CAP-002 (Chat input for quick capture).
- FE-005 (Action list for picker).

---

## PLN-008: Remove from Today

### A. User Story

> As a **User**, I want to **remove tasks from today's plan** so that I can adjust when I've overcommitted.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Swipe left or click X to remove task from today. Task returns to inbox/backlog. Confirmation not required (can re-add easily). |
| **2** | **Logic Flow** | 1. User clicks X or swipes left.<br>2. Action removed from today array.<br>3. Time budget updates.<br>4. Action remains in system (just not in today).<br>5. Can be re-added from inbox. |
| **3** | **Formal Interfaces** | **Remove Action Handler (in TodayView):**<br>```typescript<br>const handleRemove = async (actionId: string) => {<br>  // Optimistic update<br>  setTodayActions(prev => prev.filter(a => a.id !== actionId))<br>  <br>  try {<br>    await api.planning.removeFromToday(actionId)<br>    toast.success('Removed from today')<br>  } catch (err) {<br>    toast.error('Failed to remove')<br>    refetchToday()<br>  }<br>}<br>```<br><br>**Swipe to Remove (mobile):**<br>```typescript<br>import { useSwipeable } from 'react-swipeable'<br><br>function SwipeableActionCard({ action, onRemove }: Props) {<br>  const [offset, setOffset] = useState(0)<br>  <br>  const handlers = useSwipeable({<br>    onSwiping: (e) => {<br>      if (e.dir === 'Left') {<br>        setOffset(Math.min(0, e.deltaX))<br>      }<br>    },<br>    onSwipedLeft: () => {<br>      if (offset < -100) {<br>        onRemove()<br>      }<br>      setOffset(0)<br>    },<br>    trackMouse: false<br>  })<br>  <br>  return (<br>    <div className="relative overflow-hidden"><br>      {/* Delete background */}<br>      <div className="absolute inset-y-0 right-0 bg-destructive flex items-center px-4"><br>        <Trash2 className="w-5 h-5 text-white" /><br>      </div><br>      <br>      {/* Card */}<br>      <div<br>        {...handlers}<br>        style={{ transform: `translateX(${offset}px)` }}<br>        className="bg-background relative transition-transform"<br>      ><br>        <TodayActionCard action={action} onRemove={onRemove} /><br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Click X on task. Task removed from today. Time budget decreases. Swipe left (mobile). Same result. |
| **2** | **Test Logic** | **Given** task in today,<br>**When** onRemove called,<br>**Then** task removed from state.<br>**Then** API called. |
| **3** | **Formal Tests** | Render today. Click remove. Verify state update. Verify API called. |

### D. Atomicity Validation

- **Yes.** Remove functionality only.

### E. Dependencies

- PLN-002 (Today view).
- FE-002 (Optimistic updates).

---

## PLN-009: Planning Page Container

### A. User Story

> As a **User**, I want to **plan my day in a unified interface** so that I can see inbox suggestions, build my today list, and commit my plan.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Page-level container that orchestrates planning components. Fetches suggestions and today's actions. Manages selection state. Coordinates drag-drop between zones. Handles commit flow. |
| **2** | **Logic Flow** | 1. Fetch AI suggestions for inbox (max 12).<br>2. Fetch today's planned actions.<br>3. Render PLN-001 (inbox) and PLN-002 (today) side by side.<br>4. Handle drag events via PLN-003.<br>5. Update state optimistically.<br>6. On commit (PLN-005), save plan and navigate to focus. |
| **3** | **Formal Interfaces** | **PlanningPage Component (app/plan/page.tsx):**<br>```typescript<br>interface PlanningPageState {<br>  suggestions: Action[]<br>  todayActions: Action[]<br>  selectedIds: Set<string><br>  isDragging: boolean<br>  totalMinutes: number<br>}<br><br>export function PlanningPage() {<br>  const { data: suggestions } = useQuery(['suggestions'], fetchSuggestions)<br>  const { data: today } = useQuery(['today'], fetchTodayPlan)<br>  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())<br>  const router = useRouter()<br>  <br>  const totalMinutes = useMemo(() => <br>    todayActions.reduce((sum, a) => sum + (a.estimated_minutes ?? 0), 0),<br>    [todayActions]<br>  )<br>  <br>  const handleDragEnd = (result: DropResult) => {<br>    // PLN-003 logic: move between zones<br>    if (result.destination?.droppableId === 'today') {<br>      moveSuggestionToToday(result.draggableId)<br>    }<br>  }<br>  <br>  const handleCommit = async () => {<br>    await api.planning.commitDay(Array.from(selectedIds))<br>    router.push('/focus')<br>  }<br>  <br>  return (<br>    <DragDropContext onDragEnd={handleDragEnd}><br>      <div className="grid grid-cols-2 gap-4 h-full p-4"><br>        <InboxView <br>          suggestions={suggestions} <br>          selectedIds={selectedIds}<br>          onSelect={handleSelect}<br>        /><br>        <TodayView <br>          actions={today}<br>          totalMinutes={totalMinutes}<br>          onReorder={handleReorder}<br>          onRemove={handleRemove}<br>          onCommit={handleCommit}<br>        /><br>      </div><br>      <TimeBudget plannedMinutes={totalMinutes} /><br>    </DragDropContext><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open planning page. See inbox on left, today on right. Drag action to today. See it appear. Click commit. Navigate to focus mode. |
| **2** | **Test Logic** | **Given** suggestions loaded,<br>**Then** inbox displays them.<br>**When** action dragged to today,<br>**Then** today list updates.<br>**When** commit clicked,<br>**Then** API called and route changes. |
| **3** | **Formal Tests** | Mock data fetch. Test drag between zones. Test commit flow. Verify navigation. |

### D. Atomicity Validation

- **Yes.** Page orchestration only.

### E. Dependencies

- PLN-001 (Inbox View).
- PLN-002 (Today View).
- PLN-003 (Drag to Plan).
- PLN-004 (Reorder Tasks).
- PLN-005 (Day Commit).
- PLN-006 (Time Budget Display).
- PLN-007 (Add More Tasks).
- PLN-008 (Remove from Today).
- FE-001 (API Client).

### F. Complexity

**Medium** - Cross-component state, drag-drop coordination.

---

*End of Planning Specifications*
