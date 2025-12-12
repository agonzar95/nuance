# Execution Feature Specifications

**Category:** EXE (Frontend Execution)
**Total Features:** 13
**Complexity:** 7 Easy, 6 Medium, 0 Hard

---

## EXE-001: Focus Mode Container

### A. User Story

> As a **User**, I want to **enter a distraction-free focus mode** so that I can concentrate on one task at a time without visual clutter.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Full-screen container that hides navigation and non-essential UI. Displays current task prominently. Provides minimal controls: complete, stuck, pause. Subtle timer. Easy exit but with gentle friction. |
| **2** | **Logic Flow** | 1. User navigates to focus mode (from day commit or task selection).<br>2. Container takes full viewport.<br>3. Navigation hidden (navbar/tabs).<br>4. Current task displayed centrally.<br>5. Timer starts automatically.<br>6. Escape/back shows confirmation before exit. |
| **3** | **Formal Interfaces** | **FocusModeContainer Component (components/execution/FocusModeContainer.tsx):**<br>```typescript<br>interface FocusModeContainerProps {<br>  action: Action<br>  onComplete: () => void<br>  onStuck: () => void<br>  onExit: () => void<br>  children?: React.ReactNode<br>}<br><br>export function FocusModeContainer({<br>  action,<br>  onComplete,<br>  onStuck,<br>  onExit,<br>  children<br>}: FocusModeContainerProps) {<br>  const [showExitConfirm, setShowExitConfirm] = useState(false)<br>  const [elapsedSeconds, setElapsedSeconds] = useState(0)<br>  <br>  // Hide navbar on mount<br>  useEffect(() => {<br>    document.body.classList.add('focus-mode')<br>    return () => document.body.classList.remove('focus-mode')<br>  }, [])<br>  <br>  // Timer<br>  useEffect(() => {<br>    const interval = setInterval(() => {<br>      setElapsedSeconds(s => s + 1)<br>    }, 1000)<br>    return () => clearInterval(interval)<br>  }, [])<br>  <br>  // Handle escape key<br>  useEffect(() => {<br>    const handleKeyDown = (e: KeyboardEvent) => {<br>      if (e.key === 'Escape') {<br>        setShowExitConfirm(true)<br>      }<br>    }<br>    window.addEventListener('keydown', handleKeyDown)<br>    return () => window.removeEventListener('keydown', handleKeyDown)<br>  }, [])<br>  <br>  return (<br>    <div className="fixed inset-0 bg-background z-50 flex flex-col"><br>      {/* Minimal Header */}<br>      <div className="flex items-center justify-between p-4 border-b"><br>        <button<br>          onClick={() => setShowExitConfirm(true)}<br>          className="text-muted-foreground hover:text-foreground"<br>        ><br>          <ArrowLeft className="w-5 h-5" /><br>        </button><br>        <FocusTimer seconds={elapsedSeconds} /><br>        <div className="w-5" /> {/* Spacer */}<br>      </div><br>      <br>      {/* Main Content */}<br>      <div className="flex-1 flex flex-col items-center justify-center p-6"><br>        {children}<br>      </div><br>      <br>      {/* Action Bar */}<br>      <div className="p-4 border-t flex items-center justify-center gap-4"><br>        <button<br>          onClick={onStuck}<br>          className="px-6 py-3 rounded-lg border hover:bg-muted"<br>        ><br>          I'm stuck<br>        </button><br>        <button<br>          onClick={onComplete}<br>          className="px-8 py-3 rounded-lg bg-primary text-primary-foreground font-medium"<br>        ><br>          Done<br>        </button><br>      </div><br>      <br>      {/* Exit Confirmation */}<br>      <ExitConfirmDialog<br>        open={showExitConfirm}<br>        onConfirm={onExit}<br>        onCancel={() => setShowExitConfirm(false)}<br>      /><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Enter focus mode. Navigation hidden. Task visible. Timer running. Press Escape. Confirmation appears. Confirm to exit. |
| **2** | **Test Logic** | **Given** focus mode mounted,<br>**Then** body has 'focus-mode' class.<br>**When** Escape pressed,<br>**Then** exit dialog shown.<br>**When** confirmed,<br>**Then** onExit called. |
| **3** | **Formal Tests** | Render container. Verify class added. Simulate Escape. Verify dialog. Click confirm. Verify callback. |

### D. Atomicity Validation

- **Yes.** Focus mode container shell only.

### E. Dependencies

- EXE-002 (Focus task card).
- EXE-004 (Focus timer).

---

## EXE-002: Focus Task Card

### A. User Story

> As a **User**, I want to **see my current task displayed prominently** so that I know exactly what I'm working on.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Large, centered task card showing title, optional context, subtasks if any. Minimal decoration. High contrast for readability. Avoidance indicator subtle but present. |
| **2** | **Logic Flow** | 1. Receive current action.<br>2. Display title in large font.<br>3. Show context/notes if available.<br>4. Show subtasks if action has them.<br>5. Avoidance dots in corner. |
| **3** | **Formal Interfaces** | **FocusTaskCard Component (components/execution/FocusTaskCard.tsx):**<br>```typescript<br>interface FocusTaskCardProps {<br>  action: Action<br>  subtasks?: Subtask[]<br>  onSubtaskToggle?: (subtaskId: string, completed: boolean) => void<br>}<br><br>export function FocusTaskCard({<br>  action,<br>  subtasks,<br>  onSubtaskToggle<br>}: FocusTaskCardProps) {<br>  return (<br>    <div className="w-full max-w-lg space-y-6"><br>      {/* Main Task */}<br>      <div className="text-center space-y-2"><br>        <div className="flex items-center justify-center gap-2"><br>          <AvoidanceIndicator<br>            weight={action.avoidance_weight}<br>            size="lg"<br>          /><br>        </div><br>        <h1 className="text-2xl md:text-3xl font-semibold leading-tight"><br>          {action.title}<br>        </h1><br>        {action.context && (<br>          <p className="text-muted-foreground">{action.context}</p><br>        )}<br>      </div><br>      <br>      {/* Subtasks */}<br>      {subtasks && subtasks.length > 0 && (<br>        <SubtaskChecklist<br>          subtasks={subtasks}<br>          onToggle={onSubtaskToggle}<br>        /><br>      )}<br>      <br>      {/* Estimate */}<br>      {action.estimated_minutes && (<br>        <p className="text-center text-sm text-muted-foreground"><br>          Estimated: ~{action.estimated_minutes} minutes<br>        </p><br>      )}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | View focus card. See task title large and centered. See avoidance dots. See estimate if present. |
| **2** | **Test Logic** | **Given** action with title "Write report",<br>**Then** "Write report" displayed in heading.<br>**Given** avoidance_weight 4,<br>**Then** 4 dots shown. |
| **3** | **Formal Tests** | Render with action. Verify title in h1. Verify avoidance indicator. Verify estimate display. |

### D. Atomicity Validation

- **Yes.** Task card display only.

### E. Dependencies

- FE-007 (Avoidance indicator).
- EXE-003 (Subtask checklist).

---

## EXE-003: Subtask Checklist

### A. User Story

> As a **User**, I want to **see and check off subtasks** so that I can track progress through complex tasks.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Display subtasks as checkable list. Check to mark complete. Strikethrough completed items. Show progress (3/5 done). Smooth animations on check. |
| **2** | **Logic Flow** | 1. Receive subtasks array.<br>2. Display each with checkbox.<br>3. User clicks checkbox.<br>4. Toggle completed state.<br>5. Update parent via callback.<br>6. Show progress fraction. |
| **3** | **Formal Interfaces** | **SubtaskChecklist Component (components/execution/SubtaskChecklist.tsx):**<br>```typescript<br>interface Subtask {<br>  id: string<br>  title: string<br>  completed: boolean<br>  order: number<br>}<br><br>interface SubtaskChecklistProps {<br>  subtasks: Subtask[]<br>  onToggle?: (subtaskId: string, completed: boolean) => void<br>}<br><br>export function SubtaskChecklist({<br>  subtasks,<br>  onToggle<br>}: SubtaskChecklistProps) {<br>  const sortedSubtasks = [...subtasks].sort((a, b) => a.order - b.order)<br>  const completedCount = subtasks.filter(s => s.completed).length<br>  <br>  return (<br>    <div className="space-y-3"><br>      <div className="flex items-center justify-between text-sm"><br>        <span className="font-medium">Steps</span><br>        <span className="text-muted-foreground"><br>          {completedCount}/{subtasks.length} done<br>        </span><br>      </div><br>      <br>      <div className="space-y-2"><br>        {sortedSubtasks.map((subtask) => (<br>          <label<br>            key={subtask.id}<br>            className="flex items-center gap-3 cursor-pointer group"<br>          ><br>            <input<br>              type="checkbox"<br>              checked={subtask.completed}<br>              onChange={(e) => onToggle?.(subtask.id, e.target.checked)}<br>              className="sr-only"<br>            /><br>            <div<br>              className={cn(<br>                'w-5 h-5 rounded-full border-2 flex items-center justify-center',<br>                'transition-colors',<br>                subtask.completed<br>                  ? 'bg-primary border-primary'<br>                  : 'border-muted-foreground group-hover:border-primary'<br>              )}<br>            ><br>              {subtask.completed && (<br>                <Check className="w-3 h-3 text-primary-foreground" /><br>              )}<br>            </div><br>            <span<br>              className={cn(<br>                'transition-all',<br>                subtask.completed && 'line-through text-muted-foreground'<br>              )}<br>            ><br>              {subtask.title}<br>            </span><br>          </label><br>        ))}<br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | See 3 subtasks. "0/3 done" shown. Check first. Shows checkmark, strikethrough. "1/3 done". |
| **2** | **Test Logic** | **Given** 3 subtasks (0 completed),<br>**Then** "0/3 done" displayed.<br>**When** first checkbox clicked,<br>**Then** onToggle called with (id, true). |
| **3** | **Formal Tests** | Render with subtasks. Verify count display. Click checkbox. Verify callback. Verify visual state. |

### D. Atomicity Validation

- **Yes.** Subtask display and toggle only.

### E. Dependencies

- None.

---

## EXE-004: Focus Timer

### A. User Story

> As a **User**, I want to **see how long I've been working on a task** so that I have awareness without pressure.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Subtle elapsed time display. Updates every second. Format: MM:SS or H:MM:SS for longer sessions. No alarms or warnings. Can be hidden if user prefers. |
| **2** | **Logic Flow** | 1. Start timer on mount.<br>2. Increment every second.<br>3. Format based on duration.<br>4. Display in muted style.<br>5. Clean up on unmount. |
| **3** | **Formal Interfaces** | **FocusTimer Component (components/execution/FocusTimer.tsx):**<br>```typescript<br>interface FocusTimerProps {<br>  seconds: number<br>  className?: string<br>}<br><br>export function FocusTimer({ seconds, className }: FocusTimerProps) {<br>  const formatTime = (totalSeconds: number): string => {<br>    const hours = Math.floor(totalSeconds / 3600)<br>    const minutes = Math.floor((totalSeconds % 3600) / 60)<br>    const secs = totalSeconds % 60<br>    <br>    const pad = (n: number) => n.toString().padStart(2, '0')<br>    <br>    if (hours > 0) {<br>      return `${hours}:${pad(minutes)}:${pad(secs)}`<br>    }<br>    return `${pad(minutes)}:${pad(secs)}`<br>  }<br>  <br>  return (<br>    <div<br>      className={cn(<br>        'text-muted-foreground font-mono text-sm',<br>        className<br>      )}<br>    ><br>      {formatTime(seconds)}<br>    </div><br>  )<br>}<br>```<br><br>**useFocusTimer Hook:**<br>```typescript<br>export function useFocusTimer(actionId: string) {<br>  const [seconds, setSeconds] = useState(0)<br>  const [isRunning, setIsRunning] = useState(true)<br>  <br>  useEffect(() => {<br>    if (!isRunning) return<br>    <br>    const interval = setInterval(() => {<br>      setSeconds(s => s + 1)<br>    }, 1000)<br>    <br>    return () => clearInterval(interval)<br>  }, [isRunning])<br>  <br>  const pause = () => setIsRunning(false)<br>  const resume = () => setIsRunning(true)<br>  const reset = () => setSeconds(0)<br>  <br>  return { seconds, pause, resume, reset, isRunning }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Timer starts at 00:00. After 65 seconds shows 01:05. After 1 hour shows 1:00:00. |
| **2** | **Test Logic** | **Given** seconds = 0,<br>**Then** displays "00:00".<br>**Given** seconds = 3661,<br>**Then** displays "1:01:01". |
| **3** | **Formal Tests** | Render with various seconds. Verify formatted output matches expected. |

### D. Atomicity Validation

- **Yes.** Timer display only.

### E. Dependencies

- FE-008 (Timer Component - base implementation).

---

## EXE-005: Breakdown Prompt

### A. User Story

> As a **User**, I want to **be prompted to break down complex tasks** so that I can find a manageable starting point.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | When task is complex (composite/project), show prompt asking for first step. Text input for user to describe smallest action. Can skip if task is already clear. |
| **2** | **Logic Flow** | 1. Check if action complexity > atomic.<br>2. If complex and no subtasks, show prompt.<br>3. "What's the smallest first step?"<br>4. User types response.<br>5. Submit creates first subtask.<br>6. Or skip to work on task as-is. |
| **3** | **Formal Interfaces** | **BreakdownPrompt Component (components/execution/BreakdownPrompt.tsx):**<br>```typescript<br>interface BreakdownPromptProps {<br>  action: Action<br>  onSubmitStep: (step: string) => Promise<void><br>  onSkip: () => void<br>  isLoading?: boolean<br>}<br><br>export function BreakdownPrompt({<br>  action,<br>  onSubmitStep,<br>  onSkip,<br>  isLoading<br>}: BreakdownPromptProps) {<br>  const [step, setStep] = useState('')<br>  <br>  const handleSubmit = async (e: React.FormEvent) => {<br>    e.preventDefault()<br>    if (!step.trim()) return<br>    await onSubmitStep(step.trim())<br>  }<br>  <br>  return (<br>    <div className="w-full max-w-md space-y-6"><br>      <div className="text-center space-y-2"><br>        <h2 className="text-xl font-medium"><br>          This looks like a bigger task<br>        </h2><br>        <p className="text-muted-foreground"><br>          What's the smallest first step you can take?<br>        </p><br>      </div><br>      <br>      <form onSubmit={handleSubmit} className="space-y-4"><br>        <input<br>          type="text"<br>          value={step}<br>          onChange={(e) => setStep(e.target.value)}<br>          placeholder="e.g., Open the document and read the first paragraph"<br>          className="w-full px-4 py-3 rounded-lg border bg-background"<br>          autoFocus<br>          disabled={isLoading}<br>        /><br>        <br>        <div className="flex gap-3"><br>          <button<br>            type="button"<br>            onClick={onSkip}<br>            className="flex-1 py-3 rounded-lg border hover:bg-muted"<br>          ><br>            Skip for now<br>          </button><br>          <button<br>            type="submit"<br>            disabled={!step.trim() || isLoading}<br>            className="flex-1 py-3 rounded-lg bg-primary text-primary-foreground disabled:opacity-50"<br>          ><br>            {isLoading ? 'Saving...' : 'Start with this'}<br>          </button><br>        </div><br>      </form><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | See complex task. Prompt appears. Type first step. Submit. Step saved as subtask. Can skip instead. |
| **2** | **Test Logic** | **Given** prompt shown,<br>**When** step typed and submitted,<br>**Then** onSubmitStep called with text.<br>**When** Skip clicked,<br>**Then** onSkip called. |
| **3** | **Formal Tests** | Render prompt. Type step. Submit form. Verify callback. Click skip. Verify skip callback. |

### D. Atomicity Validation

- **Yes.** Breakdown prompt UI only.

### E. Dependencies

- EXE-003 (Subtask checklist for result).
- EXE-006 (First step suggestions alternative).

---

## EXE-006: First Step Suggestions

### A. User Story

> As a **User**, I want to **see AI-suggested first steps** so that I don't have to figure out where to start.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | AI generates 2-3 suggested micro-steps for complex tasks. Display as clickable options. User can select one or type their own. Selected suggestion becomes first subtask. |
| **2** | **Logic Flow** | 1. Request suggestions from AI for task.<br>2. Display loading state.<br>3. Show 2-3 suggestions as buttons.<br>4. User clicks suggestion.<br>5. Suggestion added as subtask.<br>6. Alternative: user types own step. |
| **3** | **Formal Interfaces** | **FirstStepSuggestions Component (components/execution/FirstStepSuggestions.tsx):**<br>```typescript<br>interface FirstStepSuggestionsProps {<br>  actionId: string<br>  onSelectSuggestion: (suggestion: string) => void<br>  onTypeOwn: () => void<br>}<br><br>export function FirstStepSuggestions({<br>  actionId,<br>  onSelectSuggestion,<br>  onTypeOwn<br>}: FirstStepSuggestionsProps) {<br>  const { data: suggestions, isLoading } = useQuery({<br>    queryKey: ['first-steps', actionId],<br>    queryFn: () => api.actions.getFirstStepSuggestions(actionId)<br>  })<br>  <br>  if (isLoading) {<br>    return (<br>      <div className="space-y-3"><br>        <p className="text-muted-foreground text-center"><br>          Thinking of ways to start...<br>        </p><br>        <div className="space-y-2"><br>          {[1, 2, 3].map(i => (<br>            <Skeleton key={i} className="h-12 w-full rounded-lg" /><br>          ))}<br>        </div><br>      </div><br>    )<br>  }<br>  <br>  return (<br>    <div className="space-y-4"><br>      <p className="text-muted-foreground text-center"><br>        Here are some ways to start:<br>      </p><br>      <br>      <div className="space-y-2"><br>        {suggestions?.map((suggestion, i) => (<br>          <button<br>            key={i}<br>            onClick={() => onSelectSuggestion(suggestion)}<br>            className="w-full p-4 text-left rounded-lg border hover:bg-muted transition-colors"<br>          ><br>            {suggestion}<br>          </button><br>        ))}<br>      </div><br>      <br>      <button<br>        onClick={onTypeOwn}<br>        className="w-full py-3 text-muted-foreground hover:text-foreground"<br>      ><br>        I have my own idea<br>      </button><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | View complex task. See "Thinking..." then 3 suggestions. Click one. Suggestion becomes first step. |
| **2** | **Test Logic** | **Given** suggestions loaded,<br>**Then** 3 buttons displayed.<br>**When** first clicked,<br>**Then** onSelectSuggestion called with that text. |
| **3** | **Formal Tests** | Mock API. Render component. Verify loading state. Verify suggestions appear. Click suggestion. Verify callback. |

### D. Atomicity Validation

- **Yes.** Suggestion display and selection only.

### E. Dependencies

- AGT-012 (Extract breakdown - backend).
- EXE-005 (Breakdown prompt - alternative).

---

## EXE-007: Stuck Button

### A. User Story

> As a **User**, I want to **signal when I'm stuck** so that I can get help without feeling ashamed.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Prominent but non-judgmental "I'm stuck" button in focus mode. Triggers stuck flow. Phrasing is supportive, not failure-oriented. |
| **2** | **Logic Flow** | 1. Button visible in focus mode action bar.<br>2. User clicks button.<br>3. Stuck flow initiated.<br>4. Timer pauses (optional).<br>5. Options or coaching shown. |
| **3** | **Formal Interfaces** | **StuckButton Component (components/execution/StuckButton.tsx):**<br>```typescript<br>interface StuckButtonProps {<br>  onClick: () => void<br>  variant?: 'default' | 'subtle'<br>  className?: string<br>}<br><br>export function StuckButton({<br>  onClick,<br>  variant = 'default',<br>  className<br>}: StuckButtonProps) {<br>  return (<br>    <button<br>      onClick={onClick}<br>      className={cn(<br>        'flex items-center gap-2 rounded-lg transition-colors',<br>        variant === 'default' && (<br>          'px-6 py-3 border hover:bg-muted'<br>        ),<br>        variant === 'subtle' && (<br>          'px-4 py-2 text-sm text-muted-foreground hover:text-foreground'<br>        ),<br>        className<br>      )}<br>    ><br>      <HelpCircle className="w-5 h-5" /><br>      <span>I'm stuck</span><br>    </button><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | See "I'm stuck" button. Click it. Stuck flow opens. |
| **2** | **Test Logic** | **Given** button rendered,<br>**When** clicked,<br>**Then** onClick called. |
| **3** | **Formal Tests** | Render button. Click. Verify callback fired. |

### D. Atomicity Validation

- **Yes.** Button component only.

### E. Dependencies

- EXE-008 (Stuck options - triggered by this).

---

## EXE-008: Stuck Options

### A. User Story

> As a **User**, I want to **choose what kind of help I need** so that I can quickly address what's blocking me.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Quick options for common blockers: "Too big", "Don't know how", "Don't want to", "Something else". Selection routes to appropriate help (breakdown, coaching, skip). |
| **2** | **Logic Flow** | 1. User clicks stuck button.<br>2. Options panel appears.<br>3. "Too big" → breakdown prompt.<br>4. "Don't know how" → coaching.<br>5. "Don't want to" → coaching (avoidance).<br>6. "Something else" → free-form coaching. |
| **3** | **Formal Interfaces** | **StuckOptions Component (components/execution/StuckOptions.tsx):**<br>```typescript<br>type StuckReason = 'too_big' | 'dont_know' | 'dont_want' | 'other'<br><br>interface StuckOption {<br>  id: StuckReason<br>  label: string<br>  description: string<br>  icon: React.ComponentType<br>}<br><br>const STUCK_OPTIONS: StuckOption[] = [<br>  {<br>    id: 'too_big',<br>    label: 'Too big',<br>    description: "I don't know where to start",<br>    icon: Layers<br>  },<br>  {<br>    id: 'dont_know',<br>    label: "Don't know how",<br>    description: 'I need guidance or information',<br>    icon: HelpCircle<br>  },<br>  {<br>    id: 'dont_want',<br>    label: "Don't want to",<br>    description: "I'm avoiding this task",<br>    icon: XCircle<br>  },<br>  {<br>    id: 'other',<br>    label: 'Something else',<br>    description: "Let's talk it through",<br>    icon: MessageCircle<br>  }<br>]<br><br>interface StuckOptionsProps {<br>  onSelect: (reason: StuckReason) => void<br>  onCancel: () => void<br>}<br><br>export function StuckOptions({ onSelect, onCancel }: StuckOptionsProps) {<br>  return (<br>    <div className="space-y-4"><br>      <div className="text-center"><br>        <h3 className="font-medium">What's blocking you?</h3><br>        <p className="text-sm text-muted-foreground"><br>          It's okay - let's figure this out<br>        </p><br>      </div><br>      <br>      <div className="grid grid-cols-2 gap-3"><br>        {STUCK_OPTIONS.map((option) => (<br>          <button<br>            key={option.id}<br>            onClick={() => onSelect(option.id)}<br>            className="p-4 rounded-lg border hover:bg-muted text-left transition-colors"<br>          ><br>            <option.icon className="w-5 h-5 mb-2 text-muted-foreground" /><br>            <p className="font-medium">{option.label}</p><br>            <p className="text-xs text-muted-foreground">{option.description}</p><br>          </button><br>        ))}<br>      </div><br>      <br>      <button<br>        onClick={onCancel}<br>        className="w-full py-2 text-sm text-muted-foreground hover:text-foreground"<br>      ><br>        Never mind, I'll keep trying<br>      </button><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | See 4 options. Click "Too big". Routes to breakdown. Click "Don't want to". Routes to avoidance coaching. |
| **2** | **Test Logic** | **Given** options displayed,<br>**When** "too_big" clicked,<br>**Then** onSelect called with 'too_big'. |
| **3** | **Formal Tests** | Render options. Click each. Verify correct reason passed. Click cancel. Verify cancel callback. |

### D. Atomicity Validation

- **Yes.** Stuck options selection only.

### E. Dependencies

- EXE-005 (Breakdown prompt for 'too_big').
- EXE-009 (Coaching overlay for other options).

---

## EXE-009: Coaching Overlay

### A. User Story

> As a **User**, I want to **have a supportive conversation when stuck** so that I can work through blocks without judgment.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Overlay with chat interface for coaching conversation. AI guides through the block based on stuck reason. Conversation ends with actionable next step or decision to defer. |
| **2** | **Logic Flow** | 1. Overlay opens with context (task, stuck reason).<br>2. AI sends initial supportive message.<br>3. User responds.<br>4. Multi-turn conversation.<br>5. AI suggests resolution.<br>6. User accepts or provides more context.<br>7. Overlay closes with result. |
| **3** | **Formal Interfaces** | **CoachingOverlay Component (components/execution/CoachingOverlay.tsx):**<br>```typescript<br>interface CoachingOverlayProps {<br>  action: Action<br>  stuckReason: StuckReason<br>  open: boolean<br>  onClose: () => void<br>  onResolution: (resolution: CoachingResolution) => void<br>}<br><br>type CoachingResolution =<br>  | { type: 'continue'; insight?: string }<br>  | { type: 'breakdown'; steps: string[] }<br>  | { type: 'defer'; reason: string }<br>  | { type: 'drop'; reason: string }<br><br>export function CoachingOverlay({<br>  action,<br>  stuckReason,<br>  open,<br>  onClose,<br>  onResolution<br>}: CoachingOverlayProps) {<br>  const [messages, setMessages] = useState<ChatMessage[]>([])<br>  const [input, setInput] = useState('')<br>  const [isStreaming, setIsStreaming] = useState(false)<br>  <br>  // Initialize conversation<br>  useEffect(() => {<br>    if (open && messages.length === 0) {<br>      initiateCoaching()<br>    }<br>  }, [open])<br>  <br>  const initiateCoaching = async () => {<br>    setIsStreaming(true)<br>    const response = await api.coaching.start({<br>      actionId: action.id,<br>      stuckReason<br>    })<br>    setMessages([{ role: 'assistant', content: response.message }])<br>    setIsStreaming(false)<br>  }<br>  <br>  const sendMessage = async () => {<br>    if (!input.trim()) return<br>    <br>    const userMessage = input.trim()<br>    setInput('')<br>    setMessages(prev => [...prev, { role: 'user', content: userMessage }])<br>    setIsStreaming(true)<br>    <br>    const response = await api.coaching.continue({<br>      actionId: action.id,<br>      message: userMessage<br>    })<br>    <br>    setMessages(prev => [...prev, { role: 'assistant', content: response.message }])<br>    <br>    if (response.resolution) {<br>      onResolution(response.resolution)<br>    }<br>    <br>    setIsStreaming(false)<br>  }<br>  <br>  if (!open) return null<br>  <br>  return (<br>    <div className="fixed inset-0 bg-background/95 z-50 flex flex-col"><br>      <div className="flex items-center justify-between p-4 border-b"><br>        <h2 className="font-medium">Let's work through this</h2><br>        <button onClick={onClose}><br>          <X className="w-5 h-5" /><br>        </button><br>      </div><br>      <br>      <div className="flex-1 overflow-y-auto p-4 space-y-4"><br>        {messages.map((msg, i) => (<br>          <ChatBubble key={i} message={msg} /><br>        ))}<br>        {isStreaming && <TypingIndicator />}<br>      </div><br>      <br>      <div className="p-4 border-t"><br>        <form onSubmit={(e) => { e.preventDefault(); sendMessage() }}><br>          <div className="flex gap-2"><br>            <input<br>              value={input}<br>              onChange={(e) => setInput(e.target.value)}<br>              placeholder="Type your thoughts..."<br>              className="flex-1 px-4 py-2 rounded-lg border"<br>              disabled={isStreaming}<br>            /><br>            <button<br>              type="submit"<br>              disabled={!input.trim() || isStreaming}<br>              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"<br>            ><br>              Send<br>            </button><br>          </div><br>        </form><br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open coaching. AI sends first message. Type response. AI responds. Reach resolution. Overlay closes. |
| **2** | **Test Logic** | **Given** overlay opened with 'dont_want' reason,<br>**Then** initial message received.<br>**When** user sends message,<br>**Then** AI responds.<br>**When** resolution reached,<br>**Then** onResolution called. |
| **3** | **Formal Tests** | Mock API. Open overlay. Verify init call. Send message. Verify continue call. Mock resolution response. Verify callback. |

### D. Atomicity Validation

- **Yes.** Coaching conversation UI only.

### E. Dependencies

- AGT-014 (Coaching handler - backend).
- CAP-001 (Chat message list for display).

---

## EXE-010: Complete Task Flow

### A. User Story

> As a **User**, I want to **mark a task complete with optional reflection** so that I can celebrate progress and capture learnings.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Done" button marks task complete. Optional quick note: "How did it go?" Recording actual time. Success message. Move to next task or rest screen. |
| **2** | **Logic Flow** | 1. User clicks "Done".<br>2. Optional: prompt for reflection.<br>3. Record completion time.<br>4. Update action status to 'done'.<br>5. Show success feedback.<br>6. If high avoidance, special acknowledgment.<br>7. Navigate to next task or rest. |
| **3** | **Formal Interfaces** | **CompleteTaskFlow Component (components/execution/CompleteTaskFlow.tsx):**<br>```typescript<br>interface CompleteTaskFlowProps {<br>  action: Action<br>  elapsedSeconds: number<br>  onComplete: (reflection?: string) => Promise<void><br>  onSkipReflection: () => void<br>}<br><br>export function CompleteTaskFlow({<br>  action,<br>  elapsedSeconds,<br>  onComplete,<br>  onSkipReflection<br>}: CompleteTaskFlowProps) {<br>  const [showReflection, setShowReflection] = useState(true)<br>  const [reflection, setReflection] = useState('')<br>  const [isSubmitting, setIsSubmitting] = useState(false)<br>  <br>  const handleComplete = async () => {<br>    setIsSubmitting(true)<br>    await onComplete(reflection || undefined)<br>  }<br>  <br>  const formatDuration = (seconds: number) => {<br>    const minutes = Math.round(seconds / 60)<br>    if (minutes < 60) return `${minutes} minutes`<br>    const hours = Math.floor(minutes / 60)<br>    const mins = minutes % 60<br>    return `${hours}h ${mins}m`<br>  }<br>  <br>  return (<br>    <div className="w-full max-w-md space-y-6 text-center"><br>      {/* Success Header */}<br>      <div className="space-y-2"><br>        <div className="w-16 h-16 mx-auto rounded-full bg-green-100 flex items-center justify-center"><br>          <Check className="w-8 h-8 text-green-600" /><br>        </div><br>        <h2 className="text-xl font-medium">Nice work!</h2><br>        <p className="text-muted-foreground"><br>          Completed in {formatDuration(elapsedSeconds)}<br>        </p><br>      </div><br>      <br>      {/* Optional Reflection */}<br>      {showReflection && (<br>        <div className="space-y-3"><br>          <label className="text-sm text-muted-foreground"><br>            Any thoughts on how it went? (optional)<br>          </label><br>          <textarea<br>            value={reflection}<br>            onChange={(e) => setReflection(e.target.value)}<br>            placeholder="It was easier than I expected..."<br>            className="w-full px-4 py-3 rounded-lg border resize-none"<br>            rows={3}<br>          /><br>        </div><br>      )}<br>      <br>      {/* Actions */}<br>      <div className="space-y-2"><br>        <button<br>          onClick={handleComplete}<br>          disabled={isSubmitting}<br>          className="w-full py-3 rounded-lg bg-primary text-primary-foreground font-medium"<br>        ><br>          {isSubmitting ? 'Saving...' : 'Continue'}<br>        </button><br>        {showReflection && (<br>          <button<br>            onClick={() => { setShowReflection(false); onSkipReflection() }}<br>            className="text-sm text-muted-foreground"<br>          ><br>            Skip reflection<br>          </button><br>        )}<br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Click Done. See success message with duration. Optional: add note. Click Continue. Moves to next task. |
| **2** | **Test Logic** | **Given** task completed after 30 minutes,<br>**Then** "30 minutes" displayed.<br>**When** Continue clicked,<br>**Then** onComplete called with reflection text. |
| **3** | **Formal Tests** | Render flow. Verify duration display. Enter reflection. Click continue. Verify callback with reflection. |

### D. Atomicity Validation

- **Yes.** Completion flow UI only.

### E. Dependencies

- EXE-011 (Avoidance acknowledgment for high-weight tasks).
- EXE-012 (Rest screen - next destination).

---

## EXE-011: Avoidance Acknowledgment

### A. User Story

> As a **User**, I want to **receive special acknowledgment for completing high-avoidance tasks** so that I feel recognized for pushing through difficulty.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | When completing task with avoidance weight 4+, show enhanced celebration. Acknowledge the difficulty. Supportive, non-patronizing message. Brief moment before continuing. |
| **2** | **Logic Flow** | 1. Completion flow detects high avoidance.<br>2. Show special acknowledgment instead of standard success.<br>3. Distinct visual treatment.<br>4. Message acknowledges difficulty.<br>5. Pause before continuing. |
| **3** | **Formal Interfaces** | **AvoidanceAcknowledgment Component (components/execution/AvoidanceAcknowledgment.tsx):**<br>```typescript<br>interface AvoidanceAcknowledgmentProps {<br>  action: Action<br>  onContinue: () => void<br>}<br><br>const ACKNOWLEDGMENT_MESSAGES = [<br>  "That one was hard, and you did it anyway.",<br>  "You pushed through something you'd been avoiding.",<br>  "That took real effort. Well done.",<br>  "The hard ones count extra. Nice work."<br>]<br><br>export function AvoidanceAcknowledgment({<br>  action,<br>  onContinue<br>}: AvoidanceAcknowledgmentProps) {<br>  const message = useMemo(() => {<br>    const index = Math.floor(Math.random() * ACKNOWLEDGMENT_MESSAGES.length)<br>    return ACKNOWLEDGMENT_MESSAGES[index]<br>  }, [])<br>  <br>  // Auto-continue after delay<br>  useEffect(() => {<br>    const timer = setTimeout(onContinue, 4000)<br>    return () => clearTimeout(timer)<br>  }, [onContinue])<br>  <br>  return (<br>    <div className="w-full max-w-md text-center space-y-6 animate-fade-in"><br>      {/* Enhanced Visual */}<br>      <div className="relative"><br>        <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center"><br>          <Star className="w-10 h-10 text-white" /><br>        </div><br>        <div className="absolute -inset-4 rounded-full bg-amber-400/20 animate-pulse" /><br>      </div><br>      <br>      {/* Message */}<br>      <div className="space-y-2"><br>        <h2 className="text-xl font-medium">{message}</h2><br>        <p className="text-muted-foreground"><br>          {action.title}<br>        </p><br>      </div><br>      <br>      {/* Continue */}<br>      <button<br>        onClick={onContinue}<br>        className="text-sm text-muted-foreground hover:text-foreground"<br>      ><br>        Continue<br>      </button><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Complete high-avoidance task. See special celebration with star. See supportive message. Auto-continues or tap to continue. |
| **2** | **Test Logic** | **Given** action with avoidance_weight 5,<br>**When** acknowledgment shown,<br>**Then** special message displayed.<br>**After** 4 seconds,<br>**Then** onContinue called. |
| **3** | **Formal Tests** | Render with high-avoidance action. Verify special visual. Verify message shown. Fast-forward timer. Verify callback. |

### D. Atomicity Validation

- **Yes.** Acknowledgment display only.

### E. Dependencies

- EXE-010 (Complete task flow - triggers this).

---

## EXE-012: Rest Screen

### A. User Story

> As a **User**, I want to **take a break between focus blocks** so that I can recharge without guilt.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | After completing task, option to rest. Simple screen with calming visual. Suggested rest time. "Ready to continue" button. No pressure, shame-free messaging. |
| **2** | **Logic Flow** | 1. User completes task.<br>2. Prompted: "Take a break?"<br>3. Rest screen shows countdown (optional).<br>4. Calm visual, no task info visible.<br>5. User clicks ready when done.<br>6. Navigate to next task. |
| **3** | **Formal Interfaces** | **RestScreen Component (components/execution/RestScreen.tsx):**<br>```typescript<br>interface RestScreenProps {<br>  suggestedMinutes?: number<br>  onReady: () => void<br>  onSkip: () => void<br>}<br><br>export function RestScreen({<br>  suggestedMinutes = 5,<br>  onReady,<br>  onSkip<br>}: RestScreenProps) {<br>  const [secondsRemaining, setSecondsRemaining] = useState(suggestedMinutes * 60)<br>  const [isPaused, setIsPaused] = useState(false)<br>  <br>  useEffect(() => {<br>    if (isPaused || secondsRemaining <= 0) return<br>    <br>    const interval = setInterval(() => {<br>      setSecondsRemaining(s => s - 1)<br>    }, 1000)<br>    <br>    return () => clearInterval(interval)<br>  }, [isPaused, secondsRemaining])<br>  <br>  const formatTime = (seconds: number) => {<br>    const mins = Math.floor(seconds / 60)<br>    const secs = seconds % 60<br>    return `${mins}:${secs.toString().padStart(2, '0')}`<br>  }<br>  <br>  return (<br>    <div className="fixed inset-0 bg-gradient-to-b from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800 flex flex-col items-center justify-center p-6"><br>      {/* Calming Visual */}<br>      <div className="w-32 h-32 rounded-full bg-white/50 dark:bg-white/10 flex items-center justify-center mb-8"><br>        <Coffee className="w-16 h-16 text-muted-foreground" /><br>      </div><br>      <br>      {/* Message */}<br>      <h2 className="text-2xl font-light mb-2">Take a moment</h2><br>      <p className="text-muted-foreground mb-8"><br>        You've earned a break<br>      </p><br>      <br>      {/* Timer */}<br>      {secondsRemaining > 0 ? (<br>        <div className="text-4xl font-light font-mono mb-8"><br>          {formatTime(secondsRemaining)}<br>        </div><br>      ) : (<br>        <p className="text-lg mb-8">Ready when you are</p><br>      )}<br>      <br>      {/* Actions */}<br>      <div className="space-y-3"><br>        <button<br>          onClick={onReady}<br>          className="px-8 py-3 rounded-lg bg-white dark:bg-slate-700 shadow-sm font-medium"<br>        ><br>          I'm ready to continue<br>        </button><br>        <br>        {secondsRemaining > 0 && (<br>          <button<br>            onClick={onSkip}<br>            className="block mx-auto text-sm text-muted-foreground"<br>          ><br>            Skip break<br>          </button><br>        )}<br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Complete task. Enter rest screen. See countdown from 5:00. Wait or click ready. Returns to focus mode with next task. |
| **2** | **Test Logic** | **Given** rest screen with 5 minutes,<br>**Then** "5:00" displayed.<br>**After** 1 second,<br>**Then** "4:59" displayed.<br>**When** ready clicked,<br>**Then** onReady called. |
| **3** | **Formal Tests** | Render screen. Verify initial time. Advance timer. Verify countdown. Click ready. Verify callback. Click skip. Verify skip callback. |

### D. Atomicity Validation

- **Yes.** Rest screen display only.

### E. Dependencies

- EXE-010 (Complete task flow - leads here).
- EXE-001 (Focus mode container - next destination).

---

## EXE-013: Focus Mode Page

### A. User Story

> As a **User**, I want to **work through my tasks in a guided flow** so that I move smoothly from breakdown to completion to rest.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Page-level state machine managing focus mode phases. Handles transitions between breakdown, working, stuck, coaching, completing, and rest. Fetches action data. Coordinates all execution components. |
| **2** | **Logic Flow** | 1. Fetch action by ID from route param.<br>2. If complex + no subtasks → show breakdown (EXE-005).<br>3. Else show working state (EXE-001 with EXE-002).<br>4. On stuck → show options (EXE-008) → coaching (EXE-009).<br>5. On complete → if high avoidance show EXE-011 → show rest (EXE-012).<br>6. On next → fetch next action or return to planning. |
| **3** | **Formal Interfaces** | **FocusModePage Component (app/focus/[actionId]/page.tsx):**<br>```typescript<br>type FocusPhase = <br>  | 'loading'<br>  | 'breakdown'<br>  | 'working'<br>  | 'stuck-options'<br>  | 'coaching'<br>  | 'completing'<br>  | 'avoidance-ack'<br>  | 'rest'<br><br>interface FocusPageState {<br>  phase: FocusPhase<br>  action: Action | null<br>  elapsedSeconds: number<br>  stuckReason: StuckReason | null<br>}<br><br>export function FocusModePage({ params }: { params: { actionId: string } }) {<br>  const [state, dispatch] = useReducer(focusReducer, initialState)<br>  const { data: action } = useQuery(<br>    ['action', params.actionId],<br>    () => fetchAction(params.actionId)<br>  )<br>  const router = useRouter()<br>  <br>  useEffect(() => {<br>    if (action?.is_complex && !action.subtasks?.length) {<br>      dispatch({ type: 'SET_PHASE', phase: 'breakdown' })<br>    } else {<br>      dispatch({ type: 'SET_PHASE', phase: 'working' })<br>    }<br>  }, [action])<br>  <br>  const handleStuck = (reason: StuckReason) => {<br>    dispatch({ type: 'SET_STUCK_REASON', reason })<br>    if (reason === 'too_big') {<br>      dispatch({ type: 'SET_PHASE', phase: 'breakdown' })<br>    } else {<br>      dispatch({ type: 'SET_PHASE', phase: 'coaching' })<br>    }<br>  }<br>  <br>  const handleComplete = () => {<br>    if (action.avoidance_weight >= 4) {<br>      dispatch({ type: 'SET_PHASE', phase: 'avoidance-ack' })<br>    } else {<br>      dispatch({ type: 'SET_PHASE', phase: 'rest' })<br>    }<br>  }<br>  <br>  const handleNext = async () => {<br>    const nextAction = await api.planning.getNextAction()<br>    if (nextAction) {<br>      router.push(`/focus/${nextAction.id}`)<br>    } else {<br>      router.push('/plan')<br>    }<br>  }<br>  <br>  return (<br>    <div className="min-h-screen bg-background"><br>      {state.phase === 'loading' && <LoadingSpinner />}<br>      {state.phase === 'breakdown' && (<br>        <BreakdownPrompt <br>          action={action} <br>          onComplete={() => dispatch({ type: 'SET_PHASE', phase: 'working' })}<br>        /><br>      )}<br>      {state.phase === 'working' && (<br>        <FocusModeContainer <br>          action={action}<br>          onStuck={() => dispatch({ type: 'SET_PHASE', phase: 'stuck-options' })}<br>          onComplete={handleComplete}<br>        /><br>      )}<br>      {state.phase === 'stuck-options' && (<br>        <StuckOptions <br>          onSelect={handleStuck}<br>          onCancel={() => dispatch({ type: 'SET_PHASE', phase: 'working' })}<br>        /><br>      )}<br>      {state.phase === 'coaching' && (<br>        <CoachingOverlay <br>          action={action}<br>          stuckReason={state.stuckReason}<br>          onClose={() => dispatch({ type: 'SET_PHASE', phase: 'working' })}<br>        /><br>      )}<br>      {state.phase === 'completing' && (<br>        <CompleteTaskFlow <br>          action={action}<br>          elapsedSeconds={state.elapsedSeconds}<br>          onComplete={handleComplete}<br>        /><br>      )}<br>      {state.phase === 'avoidance-ack' && (<br>        <AvoidanceAcknowledgment <br>          action={action}<br>          onContinue={() => dispatch({ type: 'SET_PHASE', phase: 'rest' })}<br>        /><br>      )}<br>      {state.phase === 'rest' && (<br>        <RestScreen <br>          onReady={handleNext}<br>          onSkip={handleNext}<br>        /><br>      )}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Navigate to focus. If complex, see breakdown. Work on task. Click stuck. See options. Get coaching. Complete task. If high avoidance, see celebration. See rest screen. Click next. |
| **2** | **Test Logic** | **Given** complex action,<br>**Then** breakdown phase shown.<br>**When** stuck clicked,<br>**Then** phase transitions to stuck-options.<br>**When** completed with avoidance >= 4,<br>**Then** avoidance-ack shown before rest. |
| **3** | **Formal Tests** | Test each phase transition. Mock action data. Verify complete flow end-to-end. |

### D. Atomicity Validation

- **Yes.** Phase state machine only. Components handle their own rendering.

### E. Dependencies

- EXE-001 (Focus Mode Container).
- EXE-002 (Focus Task Card).
- EXE-003 (Subtask Checklist).
- EXE-004 (Focus Timer).
- EXE-005 (Breakdown Prompt).
- EXE-006 (First Step Suggestions).
- EXE-007 (Stuck Button).
- EXE-008 (Stuck Options).
- EXE-009 (Coaching Overlay).
- EXE-010 (Complete Task Flow).
- EXE-011 (Avoidance Acknowledgment).
- EXE-012 (Rest Screen).
- FE-001 (API Client).

### F. Complexity

**Medium** - State machine with 8 phases.

---

*End of Execution Specifications*
