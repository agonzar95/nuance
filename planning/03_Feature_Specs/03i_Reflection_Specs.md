# Reflection Feature Specifications

**Category:** REF (Frontend Reflection)
**Total Features:** 6
**Complexity:** 5 Easy, 1 Medium, 0 Hard

---

## REF-001: EOD Trigger

### A. User Story

> As a **User**, I want to **enter end-of-day reflection at a natural time** so that I can close out my day with intention.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Time-based trigger prompts EOD reflection. Can also be triggered manually. Respects user timezone. Gentle prompt, not intrusive. |
| **2** | **Logic Flow** | 1. Check user's preferred EOD time (default 5pm).<br>2. At trigger time, show EOD prompt.<br>3. User can dismiss (remind later) or start.<br>4. Manual trigger available in navigation.<br>5. Record EOD session start. |
| **3** | **Formal Interfaces** | **useEODTrigger Hook (hooks/useEODTrigger.ts):**<br>```typescript<br>interface EODTriggerResult {<br>  shouldShowPrompt: boolean<br>  dismissPrompt: () => void<br>  startEOD: () => void<br>  snoozeMinutes: (minutes: number) => void<br>}<br><br>export function useEODTrigger(): EODTriggerResult {<br>  const { user } = useAuth()<br>  const router = useRouter()<br>  const [dismissed, setDismissed] = useState(false)<br>  const [snoozedUntil, setSnoozedUntil] = useState<Date | null>(null)<br>  <br>  const eodTime = user?.preferences?.eod_time || '17:00'<br>  <br>  const shouldShowPrompt = useMemo(() => {<br>    if (dismissed) return false<br>    if (snoozedUntil && new Date() < snoozedUntil) return false<br>    <br>    const now = new Date()<br>    const [hours, minutes] = eodTime.split(':').map(Number)<br>    const triggerTime = new Date()<br>    triggerTime.setHours(hours, minutes, 0, 0)<br>    <br>    // Show if past trigger time and not yet completed today<br>    return now >= triggerTime && !hasCompletedEODToday()<br>  }, [dismissed, snoozedUntil, eodTime])<br>  <br>  const dismissPrompt = () => setDismissed(true)<br>  <br>  const startEOD = () => {<br>    router.push('/reflect')<br>  }<br>  <br>  const snoozeMinutes = (minutes: number) => {<br>    const snoozeUntil = new Date()<br>    snoozeUntil.setMinutes(snoozeUntil.getMinutes() + minutes)<br>    setSnoozedUntil(snoozeUntil)<br>  }<br>  <br>  return { shouldShowPrompt, dismissPrompt, startEOD, snoozeMinutes }<br>}<br>```<br><br>**EODPrompt Component:**<br>```typescript<br>interface EODPromptProps {<br>  onStart: () => void<br>  onSnooze: (minutes: number) => void<br>  onDismiss: () => void<br>}<br><br>export function EODPrompt({ onStart, onSnooze, onDismiss }: EODPromptProps) {<br>  return (<br>    <div className="fixed bottom-4 right-4 max-w-sm p-4 bg-card rounded-lg shadow-lg border animate-slide-up"><br>      <div className="flex items-start gap-3"><br>        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0"><br>          <Sunset className="w-5 h-5 text-primary" /><br>        </div><br>        <div className="flex-1"><br>          <h3 className="font-medium">Time to wrap up?</h3><br>          <p className="text-sm text-muted-foreground mt-1"><br>            Let's review your day and set up for tomorrow.<br>          </p><br>          <div className="flex gap-2 mt-3"><br>            <button<br>              onClick={onStart}<br>              className="px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-md"<br>            ><br>              Start review<br>            </button><br>            <button<br>              onClick={() => onSnooze(30)}<br>              className="px-3 py-1.5 text-sm border rounded-md"<br>            ><br>              In 30 min<br>            </button><br>            <button<br>              onClick={onDismiss}<br>              className="p-1.5 text-muted-foreground"<br>            ><br>              <X className="w-4 h-4" /><br>            </button><br>          </div><br>        </div><br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | At 5pm, EOD prompt appears. Click "Start review". Goes to reflect page. Or snooze 30 min. Prompt returns later. |
| **2** | **Test Logic** | **Given** current time is after EOD time,<br>**Then** shouldShowPrompt is true.<br>**When** snoozed 30 min,<br>**Then** shouldShowPrompt is false.<br>**After** 30 min,<br>**Then** shouldShowPrompt is true again. |
| **3** | **Formal Tests** | Mock time to after EOD. Verify prompt shows. Click snooze. Verify prompt hidden. Advance time. Verify prompt returns. |

### D. Atomicity Validation

- **Yes.** EOD trigger logic only.

### E. Dependencies

- SUB-008 (Timezone handling).

**Note:** Navigates to REF-002 (Day Review Screen) but does not structurally depend on it - just a route push.

---

## REF-002: Day Review Screen

### A. User Story

> As a **User**, I want to **review what I accomplished and what's left** so that I can acknowledge progress and make decisions about remaining tasks.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Full-page review showing completed tasks, remaining tasks, and stats. Clear visual separation. Action buttons for remaining items. Positive framing regardless of completion count. |
| **2** | **Logic Flow** | 1. Fetch today's actions.<br>2. Separate completed vs remaining.<br>3. Display completed with celebration.<br>4. Display remaining with roll/drop options.<br>5. Show summary stats (count, time).<br>6. End with tomorrow prep option. |
| **3** | **Formal Interfaces** | **DayReviewScreen Component (components/reflection/DayReviewScreen.tsx):**<br>```typescript<br>interface DayReviewData {<br>  completed: Action[]<br>  remaining: Action[]<br>  totalPlanned: number<br>  totalMinutes: number<br>  highAvoidanceWins: Action[]<br>}<br><br>interface DayReviewScreenProps {<br>  data: DayReviewData<br>  onRollTask: (actionId: string) => void<br>  onDropTask: (actionId: string) => void<br>  onContinue: () => void<br>}<br><br>export function DayReviewScreen({<br>  data,<br>  onRollTask,<br>  onDropTask,<br>  onContinue<br>}: DayReviewScreenProps) {<br>  const { completed, remaining, totalPlanned, highAvoidanceWins } = data<br>  const completedCount = completed.length<br>  <br>  return (<br>    <div className="min-h-screen bg-background p-6 space-y-8"><br>      {/* Header */}<br>      <div className="text-center space-y-2"><br>        <h1 className="text-2xl font-semibold">Your Day</h1><br>        <p className="text-muted-foreground"><br>          {format(new Date(), 'EEEE, MMMM d')}<br>        </p><br>      </div><br>      <br>      {/* Stats */}<br>      <div className="flex justify-center gap-8"><br>        <div className="text-center"><br>          <div className="text-3xl font-semibold text-primary"><br>            {completedCount}<br>          </div><br>          <div className="text-sm text-muted-foreground">Completed</div><br>        </div><br>        <div className="text-center"><br>          <div className="text-3xl font-semibold">{remaining.length}</div><br>          <div className="text-sm text-muted-foreground">Remaining</div><br>        </div><br>      </div><br>      <br>      {/* High Avoidance Wins */}<br>      {highAvoidanceWins.length > 0 && (<br>        <WinHighlights wins={highAvoidanceWins} /><br>      )}<br>      <br>      {/* Completed Section */}<br>      {completed.length > 0 && (<br>        <section><br>          <h2 className="font-medium mb-3 flex items-center gap-2"><br>            <Check className="w-5 h-5 text-green-500" /><br>            Completed<br>          </h2><br>          <div className="space-y-2"><br>            {completed.map(action => (<br>              <div<br>                key={action.id}<br>                className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"<br>              ><br>                <Check className="w-4 h-4 text-green-500 shrink-0" /><br>                <span className="text-muted-foreground">{action.title}</span><br>              </div><br>            ))}<br>          </div><br>        </section><br>      )}<br>      <br>      {/* Remaining Section */}<br>      {remaining.length > 0 && (<br>        <section><br>          <h2 className="font-medium mb-3">Still on the list</h2><br>          <div className="space-y-2"><br>            {remaining.map(action => (<br>              <RemainingTaskCard<br>                key={action.id}<br>                action={action}<br>                onRoll={() => onRollTask(action.id)}<br>                onDrop={() => onDropTask(action.id)}<br>              /><br>            ))}<br>          </div><br>        </section><br>      )}<br>      <br>      {/* Continue Button */}<br>      <button<br>        onClick={onContinue}<br>        className="w-full py-4 rounded-lg bg-primary text-primary-foreground font-medium"<br>      ><br>        Continue to Summary<br>      </button><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open day review. See "3 Completed, 2 Remaining". See completed tasks with checks. See remaining with roll/drop buttons. |
| **2** | **Test Logic** | **Given** 3 completed and 2 remaining,<br>**Then** stats show "3" and "2".<br>**Then** 3 tasks in completed section.<br>**Then** 2 tasks in remaining section with controls. |
| **3** | **Formal Tests** | Render with mock data. Verify stats. Verify section counts. Click roll. Verify callback. Click drop. Verify callback. |

### D. Atomicity Validation

- **Yes.** Day review display only.

### E. Dependencies

- REF-003 (Win highlights).
- REF-005 (Roll/drop controls).
- REF-004 (Day summary - next step).

---

## REF-003: Win Highlights

### A. User Story

> As a **User**, I want to **see my high-avoidance completions celebrated** so that I feel recognized for pushing through difficult tasks.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Special section highlighting tasks with high avoidance weight that were completed. Visual distinction from regular completions. Supportive messaging about overcoming resistance. |
| **2** | **Logic Flow** | 1. Filter completed tasks with avoidance >= 4.<br>2. If any, display special "Wins" section.<br>3. Enhanced visual treatment.<br>4. Brief acknowledgment message.<br>5. List the tasks prominently. |
| **3** | **Formal Interfaces** | **WinHighlights Component (components/reflection/WinHighlights.tsx):**<br>```typescript<br>interface WinHighlightsProps {<br>  wins: Action[]<br>}<br><br>export function WinHighlights({ wins }: WinHighlightsProps) {<br>  if (wins.length === 0) return null<br>  <br>  return (<br>    <section className="relative overflow-hidden rounded-xl bg-gradient-to-br from-amber-50 to-orange-100 dark:from-amber-950/50 dark:to-orange-900/30 p-6"><br>      {/* Decorative element */}<br>      <div className="absolute top-2 right-2"><br>        <Star className="w-6 h-6 text-amber-400" /><br>      </div><br>      <br>      <div className="space-y-4"><br>        <div><br>          <h2 className="font-semibold text-lg flex items-center gap-2"><br>            <Trophy className="w-5 h-5 text-amber-500" /><br>            {wins.length === 1 ? "Today's Win" : "Today's Wins"}<br>          </h2><br>          <p className="text-sm text-muted-foreground mt-1"><br>            You pushed through {wins.length === 1 ? 'something' : 'things'} you'd been avoiding<br>          </p><br>        </div><br>        <br>        <div className="space-y-2"><br>          {wins.map(action => (<br>            <div<br>              key={action.id}<br>              className="flex items-center gap-3 p-3 rounded-lg bg-white/50 dark:bg-black/20"<br>            ><br>              <AvoidanceIndicator weight={action.avoidance_weight} /><br>              <span className="font-medium">{action.title}</span><br>            </div><br>          ))}<br>        </div><br>      </div><br>    </section><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Complete 2 high-avoidance tasks. In review, see "Today's Wins" section with trophy. Both tasks listed with avoidance dots. |
| **2** | **Test Logic** | **Given** 2 wins,<br>**Then** "Today's Wins" displayed.<br>**Then** 2 task cards in section.<br>**Given** 0 wins,<br>**Then** section not rendered. |
| **3** | **Formal Tests** | Render with wins. Verify section shows. Render with empty. Verify section hidden. |

### D. Atomicity Validation

- **Yes.** Win highlights display only.

### E. Dependencies

- FE-007 (Avoidance indicator).

---

## REF-004: Day Summary Display

### A. User Story

> As a **User**, I want to **see an AI-generated narrative of my day** so that I can appreciate my progress in context.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | AI generates 2-3 sentence summary of the day. Focuses on accomplishments and patterns. Supportive tone. Mentions high-avoidance wins if any. Streams in for engagement. |
| **2** | **Logic Flow** | 1. Request summary from AI with day data.<br>2. Stream response to display.<br>3. Show typing indicator during generation.<br>4. Display complete summary.<br>5. Option to regenerate if desired. |
| **3** | **Formal Interfaces** | **DaySummaryDisplay Component (components/reflection/DaySummaryDisplay.tsx):**<br>```typescript<br>interface DaySummaryDisplayProps {<br>  summary: string | null<br>  isLoading: boolean<br>  onRegenerate?: () => void<br>}<br><br>export function DaySummaryDisplay({<br>  summary,<br>  isLoading,<br>  onRegenerate<br>}: DaySummaryDisplayProps) {<br>  if (isLoading) {<br>    return (<br>      <div className="p-6 rounded-xl bg-muted/50 space-y-3"><br>        <div className="flex items-center gap-2 text-muted-foreground"><br>          <Sparkles className="w-5 h-5 animate-pulse" /><br>          <span>Reflecting on your day...</span><br>        </div><br>        <Skeleton className="h-4 w-full" /><br>        <Skeleton className="h-4 w-3/4" /><br>      </div><br>    )<br>  }<br>  <br>  if (!summary) {<br>    return (<br>      <div className="p-6 rounded-xl bg-muted/50 text-center text-muted-foreground"><br>        <p>Summary unavailable</p><br>      </div><br>    )<br>  }<br>  <br>  return (<br>    <div className="p-6 rounded-xl bg-gradient-to-br from-primary/5 to-primary/10 space-y-4"><br>      <div className="flex items-center gap-2"><br>        <Sparkles className="w-5 h-5 text-primary" /><br>        <span className="font-medium">Your day in summary</span><br>      </div><br>      <br>      <p className="text-lg leading-relaxed">{summary}</p><br>      <br>      {onRegenerate && (<br>        <button<br>          onClick={onRegenerate}<br>          className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"<br>        ><br>          <RefreshCw className="w-4 h-4" /><br>          Try a different summary<br>        </button><br>      )}<br>    </div><br>  )<br>}<br>```<br><br>**useDaySummary Hook:**<br>```typescript<br>export function useDaySummary(dayData: DayReviewData) {<br>  const [summary, setSummary] = useState<string | null>(null)<br>  const [isLoading, setIsLoading] = useState(false)<br>  <br>  const generateSummary = async () => {<br>    setIsLoading(true)<br>    try {<br>      const result = await api.reflection.generateSummary({<br>        completed: dayData.completed.map(a => ({<br>          title: a.title,<br>          avoidance_weight: a.avoidance_weight<br>        })),<br>        remaining: dayData.remaining.length,<br>        date: format(new Date(), 'yyyy-MM-dd')<br>      })<br>      setSummary(result.summary)<br>    } catch (err) {<br>      console.error('Failed to generate summary', err)<br>    } finally {<br>      setIsLoading(false)<br>    }<br>  }<br>  <br>  useEffect(() => {<br>    generateSummary()<br>  }, [])<br>  <br>  return { summary, isLoading, regenerate: generateSummary }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | View summary section. See loading state with sparkle. Summary appears. Can click regenerate for different version. |
| **2** | **Test Logic** | **Given** summary loading,<br>**Then** skeleton shown.<br>**When** loaded,<br>**Then** summary text displayed.<br>**When** regenerate clicked,<br>**Then** loading state shown again. |
| **3** | **Formal Tests** | Render loading state. Verify skeleton. Mock API. Verify summary displays. Click regenerate. Verify API called again. |

### D. Atomicity Validation

- **Yes.** Summary display only.

### E. Dependencies

- SUB-011 (Job: EOD Summary - generates the summary text).

**Note:** This component displays a pre-generated summary. Generation happens in SUB-011 via INT-002.

---

## REF-005: Roll/Drop Controls

### A. User Story

> As a **User**, I want to **choose to roll tasks to tomorrow or drop them** so that I can make intentional decisions about unfinished work.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Each remaining task has Roll and Drop buttons. Roll moves to tomorrow's candidates. Drop removes from active list (can still find in history). Confirmation for drop. |
| **2** | **Logic Flow** | 1. Display remaining tasks with controls.<br>2. Roll clicked → task state changes to 'rolled'.<br>3. Task will appear in tomorrow's inbox.<br>4. Drop clicked → confirm dialog.<br>5. Confirm → task state changes to 'dropped'.<br>6. Visual feedback on action. |
| **3** | **Formal Interfaces** | **RemainingTaskCard Component (components/reflection/RemainingTaskCard.tsx):**<br>```typescript<br>interface RemainingTaskCardProps {<br>  action: Action<br>  onRoll: () => void<br>  onDrop: () => void<br>}<br><br>export function RemainingTaskCard({<br>  action,<br>  onRoll,<br>  onDrop<br>}: RemainingTaskCardProps) {<br>  const [showDropConfirm, setShowDropConfirm] = useState(false)<br>  <br>  return (<br>    <div className="flex items-center gap-3 p-3 rounded-lg border bg-card"><br>      <div className="flex-1 min-w-0"><br>        <p className="font-medium truncate">{action.title}</p><br>        <div className="flex items-center gap-2 mt-1"><br>          <AvoidanceIndicator weight={action.avoidance_weight} size="sm" /><br>          {action.estimated_minutes && (<br>            <span className="text-xs text-muted-foreground"><br>              ~{action.estimated_minutes}min<br>            </span><br>          )}<br>        </div><br>      </div><br>      <br>      <div className="flex items-center gap-2"><br>        <button<br>          onClick={onRoll}<br>          className="px-3 py-1.5 text-sm rounded-md border hover:bg-muted"<br>          title="Move to tomorrow"<br>        ><br>          <ArrowRight className="w-4 h-4" /><br>        </button><br>        <button<br>          onClick={() => setShowDropConfirm(true)}<br>          className="px-3 py-1.5 text-sm rounded-md text-destructive hover:bg-destructive/10"<br>          title="Drop task"<br>        ><br>          <Trash2 className="w-4 h-4" /><br>        </button><br>      </div><br>      <br>      {/* Drop Confirmation */}<br>      <AlertDialog open={showDropConfirm} onOpenChange={setShowDropConfirm}><br>        <AlertDialogContent><br>          <AlertDialogHeader><br>            <AlertDialogTitle>Drop this task?</AlertDialogTitle><br>            <AlertDialogDescription><br>              "{action.title}" will be removed from your active list. You can still find it in history if needed.<br>            </AlertDialogDescription><br>          </AlertDialogHeader><br>          <AlertDialogFooter><br>            <AlertDialogCancel>Keep it</AlertDialogCancel><br>            <AlertDialogAction<br>              onClick={() => {<br>                onDrop()<br>                setShowDropConfirm(false)<br>              }}<br>              className="bg-destructive text-destructive-foreground"<br>            ><br>              Drop it<br>            </AlertDialogAction><br>          </AlertDialogFooter><br>        </AlertDialogContent><br>      </AlertDialog><br>    </div><br>  )<br>}<br>```<br><br>**Roll/Drop Handlers:**<br>```typescript<br>const handleRoll = async (actionId: string) => {<br>  // Optimistic update<br>  setRemaining(prev => prev.filter(a => a.id !== actionId))<br>  <br>  try {<br>    await api.actions.roll(actionId)<br>    toast.success('Rolled to tomorrow')<br>  } catch (err) {<br>    toast.error('Failed to roll task')<br>    refetchData()<br>  }<br>}<br><br>const handleDrop = async (actionId: string) => {<br>  setRemaining(prev => prev.filter(a => a.id !== actionId))<br>  <br>  try {<br>    await api.actions.drop(actionId)<br>    toast.success('Task dropped')<br>  } catch (err) {<br>    toast.error('Failed to drop task')<br>    refetchData()<br>  }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | See remaining task. Click roll arrow. Task removed, will appear tomorrow. Click trash. Confirm dialog. Confirm. Task dropped. |
| **2** | **Test Logic** | **Given** remaining task,<br>**When** roll clicked,<br>**Then** onRoll called.<br>**When** drop clicked,<br>**Then** dialog shown.<br>**When** confirmed,<br>**Then** onDrop called. |
| **3** | **Formal Tests** | Render card. Click roll. Verify callback. Click drop. Verify dialog. Confirm. Verify drop callback. |

### D. Atomicity Validation

- **Yes.** Roll/drop controls only.

### E. Dependencies

- REF-002 (Day review screen - parent).
- FE-007 (Avoidance indicator).

---

## REF-006: Tomorrow Quick Capture

### A. User Story

> As a **User**, I want to **quickly capture thoughts for tomorrow** so that I can close today with a clear mind.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | At end of reflection, option to add notes for tomorrow. Simple text input. Items go directly to inbox. Can add multiple. Quick and frictionless. |
| **2** | **Logic Flow** | 1. After summary, show quick capture section.<br>2. Text input with "Add" button.<br>3. Item submitted → added to tomorrow's inbox.<br>4. Input clears, can add more.<br>5. List shows what was captured.<br>6. "Done" to finish reflection. |
| **3** | **Formal Interfaces** | **TomorrowQuickCapture Component (components/reflection/TomorrowQuickCapture.tsx):**<br>```typescript<br>interface CapturedItem {<br>  id: string<br>  text: string<br>}<br><br>interface TomorrowQuickCaptureProps {<br>  onCapture: (text: string) => Promise<Action><br>  onDone: () => void<br>}<br><br>export function TomorrowQuickCapture({<br>  onCapture,<br>  onDone<br>}: TomorrowQuickCaptureProps) {<br>  const [input, setInput] = useState('')<br>  const [captured, setCaptured] = useState<CapturedItem[]>([])<br>  const [isCapturing, setIsCapturing] = useState(false)<br>  <br>  const handleSubmit = async (e: React.FormEvent) => {<br>    e.preventDefault()<br>    if (!input.trim() || isCapturing) return<br>    <br>    const text = input.trim()<br>    setInput('')<br>    setIsCapturing(true)<br>    <br>    try {<br>      const action = await onCapture(text)<br>      setCaptured(prev => [...prev, { id: action.id, text }])<br>    } catch (err) {<br>      toast.error('Failed to capture')<br>      setInput(text) // Restore input<br>    } finally {<br>      setIsCapturing(false)<br>    }<br>  }<br>  <br>  return (<br>    <div className="space-y-6"><br>      <div className="text-center space-y-2"><br>        <h2 className="text-xl font-medium">Anything for tomorrow?</h2><br>        <p className="text-muted-foreground"><br>          Capture thoughts so you can let go of today<br>        </p><br>      </div><br>      <br>      <form onSubmit={handleSubmit} className="flex gap-2"><br>        <input<br>          type="text"<br>          value={input}<br>          onChange={(e) => setInput(e.target.value)}<br>          placeholder="e.g., Follow up with Alex..."<br>          className="flex-1 px-4 py-3 rounded-lg border bg-background"<br>          disabled={isCapturing}<br>        /><br>        <button<br>          type="submit"<br>          disabled={!input.trim() || isCapturing}<br>          className="px-4 py-3 rounded-lg bg-primary text-primary-foreground disabled:opacity-50"<br>        ><br>          {isCapturing ? <Spinner size="sm" /> : <Plus className="w-5 h-5" />}<br>        </button><br>      </form><br>      <br>      {/* Captured Items */}<br>      {captured.length > 0 && (<br>        <div className="space-y-2"><br>          <p className="text-sm text-muted-foreground">Added for tomorrow:</p><br>          {captured.map(item => (<br>            <div<br>              key={item.id}<br>              className="flex items-center gap-2 text-sm p-2 rounded bg-muted/50"<br>            ><br>              <Check className="w-4 h-4 text-green-500" /><br>              {item.text}<br>            </div><br>          ))}<br>        </div><br>      )}<br>      <br>      {/* Done Button */}<br>      <button<br>        onClick={onDone}<br>        className="w-full py-4 rounded-lg bg-primary text-primary-foreground font-medium"<br>      ><br>        {captured.length > 0 ? 'Finish' : 'Skip for now'}<br>      </button><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | See capture input. Type thought. Click add. Item appears in list. Can add more. Click Finish. Reflection complete. |
| **2** | **Test Logic** | **Given** empty capture,<br>**When** text entered and submitted,<br>**Then** onCapture called with text.<br>**Then** item appears in list.<br>**When** Done clicked,<br>**Then** onDone called. |
| **3** | **Formal Tests** | Render component. Enter text. Submit. Verify callback. Verify list updates. Click done. Verify done callback. |

### D. Atomicity Validation

- **Yes.** Quick capture for tomorrow only.

### E. Dependencies

- CAP-002 (Chat text input - similar pattern).

**Post-completion:** User returns to capture page (home). No separate "day complete" screen for MVP.

```typescript
const handleDone = () => {
  // Mark reflection complete for today
  await api.reflection.complete()
  // Navigate to home/capture
  router.push('/capture')
}
```

---

*End of Reflection Specifications*
