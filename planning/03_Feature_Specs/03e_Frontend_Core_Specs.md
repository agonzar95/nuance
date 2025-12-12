# Frontend Core Feature Specifications

**Category:** FE (Frontend Core)
**Total Features:** 15
**Complexity:** 10 Easy, 5 Medium, 0 Hard

---

## FE-001: API Client

### A. User Story

> As a **Developer**, I want to **have a typed API client for all backend endpoints** so that frontend code has type safety and consistent error handling.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a typed TypeScript client that wraps all backend API calls. Include request/response types, automatic auth header injection, and consistent error handling. |
| **2** | **Logic Flow** | 1. Initialize client with base URL and auth token.<br>2. Define typed methods for each endpoint.<br>3. Automatically include Authorization header.<br>4. Parse responses and handle errors uniformly.<br>5. Provide hooks for React Query integration. |
| **3** | **Formal Interfaces** | **API Client (lib/api.ts):**<br>```typescript<br>import { createClient } from '@supabase/supabase-js'<br><br>interface ApiConfig {<br>  baseUrl: string<br>  getToken: () => Promise<string \| null><br>}<br><br>class ApiClient {<br>  constructor(private config: ApiConfig) {}<br>  <br>  private async request<T>(<br>    method: string,<br>    path: string,<br>    body?: unknown<br>  ): Promise<T> {<br>    const token = await this.config.getToken()<br>    const response = await fetch(`${this.config.baseUrl}${path}`, {<br>      method,<br>      headers: {<br>        'Content-Type': 'application/json',<br>        ...(token && { Authorization: `Bearer ${token}` })<br>      },<br>      body: body ? JSON.stringify(body) : undefined<br>    })<br>    <br>    if (!response.ok) {<br>      throw new ApiError(response.status, await response.json())<br>    }<br>    return response.json()<br>  }<br>  <br>  // Actions<br>  getActions(params?: ActionListParams): Promise<ActionListResponse><br>  getAction(id: string): Promise<Action><br>  updateAction(id: string, data: ActionUpdate): Promise<Action><br>  completeAction(id: string, data: CompleteActionRequest): Promise<CompleteActionResponse><br>  <br>  // Chat<br>  sendMessage(conversationId: string, content: string): Promise<MessageResponse><br>  startConversation(type: ConversationType): Promise<Conversation><br>  <br>  // Planning<br>  getSuggestions(): Promise<SuggestionResponse><br>  commitDay(actionIds: string[]): Promise<DayPlanResponse><br>}<br>```<br><br>**Types (types/api.ts):**<br>```typescript<br>export interface Action {<br>  id: string<br>  title: string<br>  description?: string<br>  status: 'active' \| 'in_progress' \| 'done' \| 'rolled' \| 'dormant'<br>  estimated_minutes?: number<br>  scheduled_date?: string<br>  avoidance_weight: number<br>  complexity: 'atomic' \| 'composite' \| 'project'<br>  created_at: string<br>  updated_at: string<br>}<br><br>export class ApiError extends Error {<br>  constructor(<br>    public status: number,<br>    public data: { error: string; details?: unknown }<br>  ) {<br>    super(data.error)<br>  }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Call api.getActions(). Get typed array. Call without auth. Get ApiError with 401. |
| **2** | **Test Logic** | **Given** valid token,<br>**When** getActions() called,<br>**Then** returns typed Action[]. |
| **3** | **Formal Tests** | Mock fetch. Verify headers include Authorization. Verify response parsing. Verify error handling for 4xx/5xx. |

### D. Atomicity Validation

- **Yes.** API client wrapper only.

### E. Dependencies

- INT-001 (Supabase client for token).
- INF-001 (Next.js project).

---

## FE-002: Optimistic Updates

### A. User Story

> As a **User**, I want to **see immediate feedback when I take actions** so that the app feels responsive.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Implement optimistic update patterns using React Query. Update UI immediately on user action, then reconcile with server response. Roll back on error. |
| **2** | **Logic Flow** | 1. User triggers action (e.g., complete task).<br>2. Immediately update local cache.<br>3. Show success state in UI.<br>4. Send request to server in background.<br>5. On success: merge server response.<br>6. On error: rollback cache, show error toast. |
| **3** | **Formal Interfaces** | **Optimistic Mutation Hook (hooks/useOptimisticMutation.ts):**<br>```typescript<br>import { useMutation, useQueryClient } from '@tanstack/react-query'<br><br>interface OptimisticConfig<TData, TVariables> {<br>  mutationFn: (vars: TVariables) => Promise<TData><br>  queryKey: string[]<br>  optimisticUpdate: (old: TData[], vars: TVariables) => TData[]<br>  onError?: (error: Error) => void<br>}<br><br>export function useOptimisticMutation<TData, TVariables>(<br>  config: OptimisticConfig<TData, TVariables><br>) {<br>  const queryClient = useQueryClient()<br>  <br>  return useMutation({<br>    mutationFn: config.mutationFn,<br>    onMutate: async (variables) => {<br>      await queryClient.cancelQueries({ queryKey: config.queryKey })<br>      const previous = queryClient.getQueryData(config.queryKey)<br>      <br>      queryClient.setQueryData(<br>        config.queryKey,<br>        (old: TData[]) => config.optimisticUpdate(old, variables)<br>      )<br>      <br>      return { previous }<br>    },<br>    onError: (err, variables, context) => {<br>      queryClient.setQueryData(config.queryKey, context?.previous)<br>      config.onError?.(err)<br>    },<br>    onSettled: () => {<br>      queryClient.invalidateQueries({ queryKey: config.queryKey })<br>    }<br>  })<br>}<br>```<br><br>**Usage Example:**<br>```typescript<br>const completeAction = useOptimisticMutation({<br>  mutationFn: (id: string) => api.completeAction(id),<br>  queryKey: ['actions', 'today'],<br>  optimisticUpdate: (actions, id) => <br>    actions.map(a => a.id === id ? { ...a, status: 'done' } : a),<br>  onError: () => toast.error('Failed to complete action')<br>})<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Complete task. UI updates immediately. Network request happens in background. On failure, task returns to previous state. |
| **2** | **Test Logic** | **Given** action in list,<br>**When** complete mutation triggered,<br>**Then** UI shows done immediately.<br>**When** server returns error,<br>**Then** UI reverts to previous state. |
| **3** | **Formal Tests** | Mock delayed API response. Verify UI updates before response. Mock error. Verify rollback. |

### D. Atomicity Validation

- **Yes.** Optimistic update pattern only.

### E. Dependencies

- FE-001 (API client).

---

## FE-003: SSE Handler

### A. User Story

> As a **User**, I want to **see AI responses stream in word-by-word** so that I get immediate feedback during conversations.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a hook that connects to Server-Sent Events endpoints and provides streaming message content. Handle connection lifecycle, reconnection, and cleanup. |
| **2** | **Logic Flow** | 1. Connect to SSE endpoint with auth.<br>2. Listen for message events.<br>3. Accumulate content as chunks arrive.<br>4. Update state on each chunk.<br>5. Handle "done" event to finalize.<br>6. Handle errors and reconnection.<br>7. Clean up on unmount. |
| **3** | **Formal Interfaces** | **SSE Hook (hooks/useSSE.ts):**<br>```typescript<br>interface SSEOptions {<br>  url: string<br>  onMessage?: (content: string) => void<br>  onComplete?: () => void<br>  onError?: (error: Error) => void<br>}<br><br>interface SSEState {<br>  content: string<br>  isStreaming: boolean<br>  error: Error \| null<br>}<br><br>export function useSSE(options: SSEOptions): SSEState & {<br>  start: () => void<br>  stop: () => void<br>} {<br>  const [state, setState] = useState<SSEState>({<br>    content: '',<br>    isStreaming: false,<br>    error: null<br>  })<br>  const eventSourceRef = useRef<EventSource \| null>(null)<br>  <br>  const start = useCallback(async () => {<br>    const token = await getToken()<br>    const url = new URL(options.url)<br>    url.searchParams.set('token', token)<br>    <br>    const eventSource = new EventSource(url.toString())<br>    eventSourceRef.current = eventSource<br>    <br>    setState(s => ({ ...s, isStreaming: true, content: '' }))<br>    <br>    eventSource.addEventListener('message', (e) => {<br>      const { content } = JSON.parse(e.data)<br>      setState(s => ({ ...s, content: s.content + content }))<br>      options.onMessage?.(content)<br>    })<br>    <br>    eventSource.addEventListener('done', () => {<br>      eventSource.close()<br>      setState(s => ({ ...s, isStreaming: false }))<br>      options.onComplete?.()    })<br>    <br>    eventSource.addEventListener('error', (e) => {<br>      const error = new Error('SSE connection failed')<br>      setState(s => ({ ...s, isStreaming: false, error }))<br>      options.onError?.(error)<br>    })<br>  }, [options])<br>  <br>  const stop = useCallback(() => {<br>    eventSourceRef.current?.close()<br>    setState(s => ({ ...s, isStreaming: false }))<br>  }, [])<br>  <br>  useEffect(() => {<br>    return () => eventSourceRef.current?.close()<br>  }, [])<br>  <br>  return { ...state, start, stop }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Start streaming. See content appear incrementally. Stream completes. Content is final. |
| **2** | **Test Logic** | **Given** SSE endpoint,<br>**When** start() called,<br>**Then** isStreaming is true.<br>**When** message events arrive,<br>**Then** content accumulates.<br>**When** done event arrives,<br>**Then** isStreaming is false. |
| **3** | **Formal Tests** | Mock EventSource. Fire message events. Verify content updates. Fire done event. Verify final state. |

### D. Atomicity Validation

- **Yes.** SSE handling only.

### E. Dependencies

- AGT-006 (Backend SSE endpoint).
- FE-001 (API client for token).

---

## FE-004: Real-time Handler

### A. User Story

> As a **User**, I want to **see updates from other devices in real-time** so that my data is always synchronized.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Subscribe to Supabase real-time channels for action updates. Automatically sync changes from any source (other tabs, Telegram, etc.) to the UI. |
| **2** | **Logic Flow** | 1. On mount, subscribe to user's actions channel.<br>2. Listen for INSERT, UPDATE, DELETE events.<br>3. Update React Query cache on changes.<br>4. Handle subscription errors gracefully.<br>5. Cleanup subscription on unmount. |
| **3** | **Formal Interfaces** | **Real-time Hook (hooks/useRealtimeActions.ts):**<br>```typescript<br>import { useEffect } from 'react'<br>import { useQueryClient } from '@tanstack/react-query'<br>import { supabase } from '@/lib/supabase'<br><br>export function useRealtimeActions(userId: string) {<br>  const queryClient = useQueryClient()<br>  <br>  useEffect(() => {<br>    const channel = supabase<br>      .channel(`actions:${userId}`)<br>      .on(<br>        'postgres_changes',<br>        {<br>          event: '*',<br>          schema: 'public',<br>          table: 'actions',<br>          filter: `user_id=eq.${userId}`<br>        },<br>        (payload) => {<br>          switch (payload.eventType) {<br>            case 'INSERT':<br>              queryClient.setQueryData(<br>                ['actions'],<br>                (old: Action[]) => [...(old ?? []), payload.new]<br>              )<br>              break<br>            case 'UPDATE':<br>              queryClient.setQueryData(<br>                ['actions'],<br>                (old: Action[]) => old?.map(a => <br>                  a.id === payload.new.id ? payload.new : a<br>                )<br>              )<br>              break<br>            case 'DELETE':<br>              queryClient.setQueryData(<br>                ['actions'],<br>                (old: Action[]) => old?.filter(a => a.id !== payload.old.id)<br>              )<br>              break<br>          }<br>        }<br>      )<br>      .subscribe()<br>    <br>    return () => {<br>      supabase.removeChannel(channel)<br>    }<br>  }, [userId, queryClient])<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open app in two tabs. Create action in one. See it appear in the other. |
| **2** | **Test Logic** | **Given** subscribed to channel,<br>**When** INSERT event received,<br>**Then** new action appears in cache.<br>**When** UPDATE event received,<br>**Then** action updates in cache. |
| **3** | **Formal Tests** | Mock Supabase channel. Emit postgres_changes events. Verify React Query cache updates. |

### D. Atomicity Validation

- **Yes.** Real-time subscription only.

### E. Dependencies

- INT-001 (Supabase client).
- SUB-013 (Real-time subscriptions configured).

---

## FE-005: Action List Component

### A. User Story

> As a **User**, I want to **see my actions in a list** so that I can browse and manage them.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a reusable action list component that displays actions with their metadata. Support sorting, filtering by status, and click-to-expand. |
| **2** | **Logic Flow** | 1. Receive actions array as prop.<br>2. Render each action as ActionCard.<br>3. Apply any filter/sort props.<br>4. Handle empty state.<br>5. Support selection callback. |
| **3** | **Formal Interfaces** | **ActionList Component (components/actions/ActionList.tsx):**<br>```typescript<br>interface ActionListProps {<br>  actions: Action[]<br>  onActionClick?: (action: Action) => void<br>  emptyMessage?: string<br>  showAvoidance?: boolean<br>  showEstimate?: boolean<br>  variant?: 'default' \| 'compact' \| 'planning'<br>}<br><br>export function ActionList({<br>  actions,<br>  onActionClick,<br>  emptyMessage = 'No actions',<br>  showAvoidance = true,<br>  showEstimate = true,<br>  variant = 'default'<br>}: ActionListProps) {<br>  if (actions.length === 0) {<br>    return <EmptyState message={emptyMessage} /><br>  }<br>  <br>  return (<br>    <ul className="space-y-2" role="list"><br>      {actions.map(action => (<br>        <li key={action.id}><br>          <ActionCard<br>            action={action}<br>            onClick={() => onActionClick?.(action)}<br>            showAvoidance={showAvoidance}<br>            showEstimate={showEstimate}<br>            variant={variant}<br>          /><br>        </li><br>      ))}<br>    </ul><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Pass 5 actions. See 5 cards. Pass empty array. See empty message. Click action. Callback fires. |
| **2** | **Test Logic** | **Given** 3 actions,<br>**When** rendered,<br>**Then** 3 list items visible.<br>**Given** empty array,<br>**Then** empty message shown. |
| **3** | **Formal Tests** | Render with mock actions. Query for list items. Verify count. Click item. Verify callback called with action. |

### D. Atomicity Validation

- **Yes.** List rendering only.

### E. Dependencies

- FE-006 (ActionCard component).
- FE-010 (Empty state component).

---

## FE-006: Action Card Component

### A. User Story

> As a **User**, I want to **see actions displayed as cards with key information** so that I can quickly understand what needs to be done.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a card component for a single action. Display title, avoidance weight, time estimate, and status. Support compact and expanded variants. |
| **2** | **Logic Flow** | 1. Receive action as prop.<br>2. Display title prominently.<br>3. Show avoidance dots (1-5).<br>4. Show time estimate.<br>5. Apply status-based styling.<br>6. Support click/tap interaction. |
| **3** | **Formal Interfaces** | **ActionCard Component (components/actions/ActionCard.tsx):**<br>```typescript<br>interface ActionCardProps {<br>  action: Action<br>  onClick?: () => void<br>  showAvoidance?: boolean<br>  showEstimate?: boolean<br>  variant?: 'default' \| 'compact' \| 'focus'<br>  draggable?: boolean<br>}<br><br>export function ActionCard({<br>  action,<br>  onClick,<br>  showAvoidance = true,<br>  showEstimate = true,<br>  variant = 'default'<br>}: ActionCardProps) {<br>  return (<br>    <div<br>      className={cn(<br>        'rounded-lg border bg-card p-4 cursor-pointer',<br>        'hover:shadow-md transition-shadow',<br>        variant === 'compact' && 'p-2',<br>        variant === 'focus' && 'p-6 text-center'<br>      )}<br>      onClick={onClick}<br>      role="button"<br>      tabIndex={0}<br>    ><br>      <h3 className={cn(<br>        'font-medium',<br>        variant === 'focus' && 'text-xl'<br>      )}><br>        {action.title}<br>      </h3><br>      <br>      <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground"><br>        {showAvoidance && (<br>          <AvoidanceIndicator weight={action.avoidance_weight} /><br>        )}<br>        {showEstimate && action.estimated_minutes && (<br>          <span>~{action.estimated_minutes}min</span><br>        )}<br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Render card. See title, avoidance dots, time. Click card. Callback fires. |
| **2** | **Test Logic** | **Given** action with title "Buy milk", avoidance 3, estimate 15,<br>**When** rendered,<br>**Then** title visible, 3 filled dots, "~15min" text. |
| **3** | **Formal Tests** | Render with mock action. Query for title text. Query for avoidance indicator. Query for estimate. |

### D. Atomicity Validation

- **Yes.** Card display only.

### E. Dependencies

- FE-007 (Avoidance indicator).

---

## FE-007: Avoidance Indicator

### A. User Story

> As a **User**, I want to **see a visual indicator of task difficulty** so that I know which tasks carry emotional weight.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a dot-based indicator that shows avoidance weight from 1-5. Filled dots represent the weight level. Keep styling subtle but visible. |
| **2** | **Logic Flow** | 1. Receive weight (1-5) as prop.<br>2. Render 5 dots total.<br>3. Fill first N dots based on weight.<br>4. Apply consistent styling. |
| **3** | **Formal Interfaces** | **AvoidanceIndicator Component (components/ui/AvoidanceIndicator.tsx):**<br>```typescript<br>interface AvoidanceIndicatorProps {<br>  weight: number // 1-5<br>  size?: 'sm' \| 'md' \| 'lg'<br>}<br><br>export function AvoidanceIndicator({<br>  weight,<br>  size = 'sm'<br>}: AvoidanceIndicatorProps) {<br>  const clampedWeight = Math.min(5, Math.max(1, weight))<br>  <br>  const sizeClasses = {<br>    sm: 'w-1.5 h-1.5',<br>    md: 'w-2 h-2',<br>    lg: 'w-2.5 h-2.5'<br>  }<br>  <br>  return (<br>    <div <br>      className="flex gap-0.5" <br>      role="img" <br>      aria-label={`Avoidance weight: ${clampedWeight} of 5`}<br>    ><br>      {Array.from({ length: 5 }).map((_, i) => (<br>        <span<br>          key={i}<br>          className={cn(<br>            'rounded-full',<br>            sizeClasses[size],<br>            i < clampedWeight<br>              ? 'bg-foreground/60'<br>              : 'bg-muted-foreground/20'<br>          )}<br>        /><br>      ))}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Weight 3 shows 3 filled dots and 2 empty. Weight 5 shows all filled. Weight 1 shows 1 filled and 4 empty. |
| **2** | **Test Logic** | **Given** weight=3,<br>**When** rendered,<br>**Then** 3 dots have filled class, 2 have empty class. |
| **3** | **Formal Tests** | Render with weight 3. Count filled vs empty dots. Verify aria-label. |

### D. Atomicity Validation

- **Yes.** Visual indicator only.

### E. Dependencies

- None.

---

## FE-008: Timer Component

### A. User Story

> As a **User**, I want to **see a timer during focus sessions** so that I have a sense of time passing without clock-watching.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a timer component that displays elapsed or remaining time. Support subtle styling that doesn't distract. Optional notification at interval. |
| **2** | **Logic Flow** | 1. Receive start time or duration.<br>2. Update display every second.<br>3. Calculate elapsed or remaining.<br>4. Format as MM:SS.<br>5. Optionally fire callback at threshold. |
| **3** | **Formal Interfaces** | **Timer Component (components/ui/Timer.tsx):**<br>```typescript<br>interface TimerProps {<br>  mode: 'elapsed' \| 'countdown'<br>  startTime?: Date<br>  durationMinutes?: number<br>  onComplete?: () => void<br>  onThreshold?: (minutes: number) => void<br>  thresholdMinutes?: number<br>  className?: string<br>}<br><br>export function Timer({<br>  mode,<br>  startTime = new Date(),<br>  durationMinutes = 25,<br>  onComplete,<br>  onThreshold,<br>  thresholdMinutes = 25,<br>  className<br>}: TimerProps) {<br>  const [seconds, setSeconds] = useState(0)<br>  const thresholdFiredRef = useRef(false)<br>  <br>  useEffect(() => {<br>    const interval = setInterval(() => {<br>      const elapsed = Math.floor(<br>        (Date.now() - startTime.getTime()) / 1000<br>      )<br>      setSeconds(elapsed)<br>      <br>      const minutes = Math.floor(elapsed / 60)<br>      if (minutes >= thresholdMinutes && !thresholdFiredRef.current) {<br>        thresholdFiredRef.current = true<br>        onThreshold?.(minutes)<br>      }<br>      <br>      if (mode === 'countdown') {<br>        const remaining = durationMinutes * 60 - elapsed<br>        if (remaining <= 0) {<br>          onComplete?.()          clearInterval(interval)<br>        }<br>      }<br>    }, 1000)<br>    <br>    return () => clearInterval(interval)<br>  }, [startTime, durationMinutes, mode])<br>  <br>  const displaySeconds = mode === 'countdown'<br>    ? Math.max(0, durationMinutes * 60 - seconds)<br>    : seconds<br>  <br>  const minutes = Math.floor(displaySeconds / 60)<br>  const secs = displaySeconds % 60<br>  <br>  return (<br>    <div className={cn('font-mono text-2xl text-muted-foreground', className)}><br>      {String(minutes).padStart(2, '0')}:{String(secs).padStart(2, '0')}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Start timer. See time increment each second. Countdown reaches zero. onComplete fires. |
| **2** | **Test Logic** | **Given** mode="elapsed",<br>**When** 65 seconds pass,<br>**Then** displays "01:05". |
| **3** | **Formal Tests** | Mock timers. Advance time. Verify display updates. Verify callbacks fire at thresholds. |

### D. Atomicity Validation

- **Yes.** Timer display only.

### E. Dependencies

- None.

---

## FE-009: Loading States

### A. User Story

> As a **User**, I want to **see loading indicators** so that I know the app is working when things take time.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create reusable loading components: spinner, skeleton cards, and full-page loader. Keep animations subtle and calming. |
| **2** | **Logic Flow** | 1. Spinner for inline loading.<br>2. Skeleton for content placeholders.<br>3. PageLoader for route transitions.<br>4. Match content layout in skeletons. |
| **3** | **Formal Interfaces** | **Loading Components (components/ui/Loading.tsx):**<br>```typescript<br>// Spinner<br>export function Spinner({ size = 'md' }: { size?: 'sm' \| 'md' \| 'lg' }) {<br>  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }<br>  return (<br>    <div <br>      className={cn('animate-spin rounded-full border-2 border-muted border-t-foreground', sizes[size])}<br>      role="status"<br>      aria-label="Loading"<br>    /><br>  )<br>}<br><br>// Skeleton<br>export function Skeleton({ className }: { className?: string }) {<br>  return (<br>    <div className={cn('animate-pulse bg-muted rounded', className)} /><br>  )<br>}<br><br>// Action Card Skeleton<br>export function ActionCardSkeleton() {<br>  return (<br>    <div className="rounded-lg border bg-card p-4"><br>      <Skeleton className="h-5 w-3/4 mb-2" /><br>      <Skeleton className="h-4 w-1/4" /><br>    </div><br>  )<br>}<br><br>// Page Loader<br>export function PageLoader() {<br>  return (<br>    <div className="flex items-center justify-center min-h-screen"><br>      <Spinner size="lg" /><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Render Spinner. See animated circle. Render Skeleton. See pulsing placeholder. |
| **2** | **Test Logic** | **Given** Spinner rendered,<br>**Then** has role="status" and aria-label. |
| **3** | **Formal Tests** | Render each component. Verify accessibility attributes. Verify animations applied. |

### D. Atomicity Validation

- **Yes.** Loading UI components only.

### E. Dependencies

- None.

---

## FE-010: Empty States

### A. User Story

> As a **User**, I want to **see helpful messages when lists are empty** so that I'm not confused by blank screens.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create empty state components for different contexts: inbox, today, actions. Include encouraging message and optional action button. |
| **2** | **Logic Flow** | 1. Display context-appropriate message.<br>2. Show optional illustration/icon.<br>3. Provide action button if applicable.<br>4. Keep tone positive without toxic positivity. |
| **3** | **Formal Interfaces** | **Empty State Component (components/ui/EmptyState.tsx):**<br>```typescript<br>interface EmptyStateProps {<br>  title?: string<br>  message: string<br>  icon?: ReactNode<br>  action?: {<br>    label: string<br>    onClick: () => void<br>  }<br>}<br><br>export function EmptyState({<br>  title,<br>  message,<br>  icon,<br>  action<br>}: EmptyStateProps) {<br>  return (<br>    <div className="flex flex-col items-center justify-center py-12 text-center"><br>      {icon && (<br>        <div className="mb-4 text-muted-foreground">{icon}</div><br>      )}<br>      {title && (<br>        <h3 className="font-medium text-lg mb-2">{title}</h3><br>      )}<br>      <p className="text-muted-foreground max-w-sm">{message}</p><br>      {action && (<br>        <button<br>          onClick={action.onClick}<br>          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"<br>        ><br>          {action.label}<br>        </button><br>      )}<br>    </div><br>  )<br>}<br><br>// Pre-configured variants<br>export function EmptyInbox() {<br>  return (<br>    <EmptyState<br>      title="Inbox is clear"<br>      message="Nothing waiting for your attention. Enjoy the calm."<br>    /><br>  )<br>}<br><br>export function EmptyToday() {<br>  return (<br>    <EmptyState<br>      title="No plan yet"<br>      message="Drag some tasks from inbox to start your day."<br>    /><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Empty inbox shows "Inbox is clear" message. Empty today shows guidance to drag tasks. |
| **2** | **Test Logic** | **Given** EmptyInbox rendered,<br>**Then** displays title and message. |
| **3** | **Formal Tests** | Render each variant. Verify text content. Verify action button if present. |

### D. Atomicity Validation

- **Yes.** Empty state display only.

### E. Dependencies

- None.

---

## FE-011: Offline Awareness

### A. User Story

> As a **User**, I want to **know when I'm offline** so that I understand why some features might not work.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Detect network status changes. Show subtle banner when offline. Hide when back online. Queue failed requests for retry. |
| **2** | **Logic Flow** | 1. Listen to online/offline events.<br>2. Update global state.<br>3. Show/hide offline banner.<br>4. Optionally queue mutations.<br>5. Retry queued items when online. |
| **3** | **Formal Interfaces** | **Offline Hook & Banner (hooks/useOffline.ts):**<br>```typescript<br>export function useOffline() {<br>  const [isOffline, setIsOffline] = useState(!navigator.onLine)<br>  <br>  useEffect(() => {<br>    const handleOnline = () => setIsOffline(false)<br>    const handleOffline = () => setIsOffline(true)<br>    <br>    window.addEventListener('online', handleOnline)<br>    window.addEventListener('offline', handleOffline)<br>    <br>    return () => {<br>      window.removeEventListener('online', handleOnline)<br>      window.removeEventListener('offline', handleOffline)<br>    }<br>  }, [])<br>  <br>  return isOffline<br>}<br>```<br><br>**Offline Banner (components/ui/OfflineBanner.tsx):**<br>```typescript<br>export function OfflineBanner() {<br>  const isOffline = useOffline()<br>  <br>  if (!isOffline) return null<br>  <br>  return (<br>    <div className="fixed top-0 left-0 right-0 bg-warning text-warning-foreground py-2 px-4 text-center text-sm z-50"><br>      You're offline. Changes will sync when you're back online.<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Go offline. See banner. Go online. Banner disappears. |
| **2** | **Test Logic** | **Given** navigator.onLine = false,<br>**Then** banner visible.<br>**When** online event fires,<br>**Then** banner hidden. |
| **3** | **Formal Tests** | Mock navigator.onLine. Render banner. Verify visibility. Fire events. Verify state changes. |

### D. Atomicity Validation

- **Yes.** Offline detection only.

### E. Dependencies

- None.

---

## FE-012: PWA Manifest

### A. User Story

> As a **User**, I want to **install the app on my device** so that I can access it like a native app.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Configure web app manifest with name, icons, colors, and display mode. Enable standalone mode for installability. |
| **2** | **Logic Flow** | 1. Create manifest.json with app metadata.<br>2. Add icons in multiple sizes.<br>3. Configure theme and background colors.<br>4. Set display mode to standalone.<br>5. Link manifest in HTML head. |
| **3** | **Formal Interfaces** | **Manifest (public/manifest.json):**<br>```json<br>{<br>  "name": "Executive Function Prosthetic",<br>  "short_name": "EFP",<br>  "description": "AI-powered productivity for minds that work differently",<br>  "start_url": "/",<br>  "display": "standalone",<br>  "background_color": "#FAFAF9",<br>  "theme_color": "#3B82F6",<br>  "icons": [<br>    {<br>      "src": "/icons/icon-192.png",<br>      "sizes": "192x192",<br>      "type": "image/png"<br>    },<br>    {<br>      "src": "/icons/icon-512.png",<br>      "sizes": "512x512",<br>      "type": "image/png"<br>    },<br>    {<br>      "src": "/icons/icon-maskable-512.png",<br>      "sizes": "512x512",<br>      "type": "image/png",<br>      "purpose": "maskable"<br>    }<br>  ]<br>}<br>```<br><br>**Next.js Config (next.config.js):**<br>```javascript<br>const withPWA = require('next-pwa')({<br>  dest: 'public',<br>  disable: process.env.NODE_ENV === 'development'<br>})<br><br>module.exports = withPWA({<br>  // other config<br>})<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Visit site. See install prompt (on mobile/desktop). Install. App opens in standalone mode. |
| **2** | **Test Logic** | **Given** manifest linked correctly,<br>**When** Lighthouse PWA audit runs,<br>**Then** installable criteria pass. |
| **3** | **Formal Tests** | Validate manifest.json schema. Run Lighthouse. Verify PWA score > 90. |

### D. Atomicity Validation

- **Yes.** Manifest configuration only.

### E. Dependencies

- INF-001 (Next.js project).

---

## FE-013: Service Worker

### A. User Story

> As a **User**, I want to **use the app even with spotty connectivity** so that I can capture thoughts anytime.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Implement service worker for basic caching. Cache app shell and static assets. Provide offline fallback page. Queue failed API requests for retry. |
| **2** | **Logic Flow** | 1. Register service worker on load.<br>2. Cache app shell on install.<br>3. Serve cached assets when offline.<br>4. Show offline page for uncached routes.<br>5. Use stale-while-revalidate for API calls. |
| **3** | **Formal Interfaces** | **Service Worker (public/sw.js via next-pwa):**<br>```javascript<br>// next-pwa generates this, but we can customize<br>// Caching strategies configured in next.config.js<br><br>// Custom offline fallback<br>self.addEventListener('fetch', (event) => {<br>  if (event.request.mode === 'navigate') {<br>    event.respondWith(<br>      fetch(event.request).catch(() => {<br>        return caches.match('/offline')<br>      })<br>    )<br>  }<br>})<br>```<br><br>**PWA Config (next.config.js):**<br>```javascript<br>const withPWA = require('next-pwa')({<br>  dest: 'public',<br>  disable: process.env.NODE_ENV === 'development',<br>  runtimeCaching: [<br>    {<br>      urlPattern: /^https:\/\/api\..*\/v1\/.*/,<br>      handler: 'NetworkFirst',<br>      options: {<br>        cacheName: 'api-cache',<br>        expiration: {<br>          maxEntries: 50,<br>          maxAgeSeconds: 300<br>        }<br>      }<br>    },<br>    {<br>      urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,<br>      handler: 'CacheFirst',<br>      options: {<br>        cacheName: 'image-cache',<br>        expiration: {<br>          maxEntries: 100,<br>          maxAgeSeconds: 86400<br>        }<br>      }<br>    }<br>  ]<br>})<br>```<br><br>**Offline Page (app/offline/page.tsx):**<br>```typescript<br>export default function OfflinePage() {<br>  return (<br>    <div className="flex flex-col items-center justify-center min-h-screen p-4"><br>      <h1 className="text-2xl font-medium mb-4">You're offline</h1><br>      <p className="text-muted-foreground text-center"><br>        We'll sync your changes when you're back online.<br>      </p><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Load app. Go offline. Refresh. See offline page or cached content. Go online. Content syncs. |
| **2** | **Test Logic** | **Given** app shell cached,<br>**When** offline and navigating,<br>**Then** cached pages load.<br>**When** uncached route requested,<br>**Then** offline page shown. |
| **3** | **Formal Tests** | Verify service worker registers. Verify caches created. Simulate offline. Verify fallback behavior. |

### D. Atomicity Validation

- **Yes.** Service worker caching only.

### E. Dependencies

- FE-012 (PWA manifest).
- FE-011 (Offline awareness).

---

## FE-014: Responsive Layout

### A. User Story

> As a **User**, I want to **use the app on any device** so that I can capture and plan whether on phone, tablet, or desktop.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Implement responsive layouts using Tailwind breakpoints. Desktop: side navbar. Tablet: collapsible navbar. Mobile: bottom tabs. Adjust spacing and typography. |
| **2** | **Logic Flow** | 1. Define breakpoints: mobile (<768), tablet (768-1024), desktop (>1024).<br>2. Use Tailwind responsive prefixes.<br>3. Conditional render navbar vs bottom tabs.<br>4. Adjust grid columns per breakpoint.<br>5. Scale touch targets for mobile. |
| **3** | **Formal Interfaces** | **Layout Component (components/layout/AppLayout.tsx):**<br>```typescript<br>export function AppLayout({ children }: { children: ReactNode }) {<br>  return (<br>    <div className="min-h-screen bg-background"><br>      {/* Desktop/Tablet: Side navbar */}<br>      <div className="hidden md:flex"<br>        <Navbar /><br>        <main className="flex-1 p-6">{children}</main><br>      </div><br>      <br>      {/* Mobile: Bottom tabs */}<br>      <div className="md:hidden"<br>        <main className="pb-16 p-4">{children}</main><br>        <BottomTabs /><br>      </div><br>      <br>      <OfflineBanner /><br>    </div><br>  )<br>}<br>```<br><br>**Responsive Grid (components/ui/Grid.tsx):**<br>```typescript<br>interface GridProps {<br>  children: ReactNode<br>  cols?: { mobile?: number; tablet?: number; desktop?: number }<br>}<br><br>export function Grid({ <br>  children, <br>  cols = { mobile: 1, tablet: 2, desktop: 3 } <br>}: GridProps) {<br>  return (<br>    <div className={cn(<br>      'grid gap-4',<br>      `grid-cols-${cols.mobile}`,<br>      `md:grid-cols-${cols.tablet}`,<br>      `lg:grid-cols-${cols.desktop}`<br>    )}><br>      {children}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | View on mobile. See bottom tabs. View on desktop. See side navbar. Content adjusts. |
| **2** | **Test Logic** | **Given** viewport < 768px,<br>**Then** bottom tabs visible, side navbar hidden.<br>**Given** viewport > 1024px,<br>**Then** side navbar visible, bottom tabs hidden. |
| **3** | **Formal Tests** | Render at different viewport sizes. Query for navbar vs bottom tabs. Verify correct visibility. |

### D. Atomicity Validation

- **Yes.** Responsive layout only.

### E. Dependencies

- FE-015 (Navigation component).
- INF-001 (Next.js + Tailwind).

---

## FE-015: Navigation Component

### A. User Story

> As a **User**, I want to **navigate between screens** so that I can access Capture, Plan, Focus, and Reflect.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create navigation components for both desktop (side navbar) and mobile (bottom tabs). Highlight active route. Include quick add button. |
| **2** | **Logic Flow** | 1. Get current route.<br>2. Render nav items with icons.<br>3. Highlight active item.<br>4. Handle click to navigate.<br>5. Position based on device. |
| **3** | **Formal Interfaces** | **Navbar (components/layout/Navbar.tsx):**<br>```typescript<br>const navItems = [<br>  { href: '/capture', label: 'Capture', icon: MessageSquare },<br>  { href: '/plan', label: 'Plan', icon: Calendar },<br>  { href: '/focus', label: 'Focus', icon: Target },<br>  { href: '/reflect', label: 'Reflect', icon: BarChart }<br>]<br>// Note: Canvas feature deferred to post-MVP. Using standard page navigation for v1.<br><br>export function Navbar() {<br>  const pathname = usePathname()<br>  <br>  return (<br>    <nav className="w-20 border-r bg-background flex flex-col items-center py-4 gap-2"><br>      {navItems.map(item => (<br>        <Link<br>          key={item.href}<br>          href={item.href}<br>          className={cn(<br>            'flex flex-col items-center p-3 rounded-lg',<br>            'hover:bg-muted transition-colors',<br>            pathname === item.href && 'bg-muted text-primary'<br>          )}<br>        ><br>          <item.icon className="w-6 h-6" /><br>          <span className="text-xs mt-1">{item.label}</span><br>        </Link><br>      ))}<br>      <br>      <div className="flex-1" /><br>      <br>      <QuickAddButton /><br>    </nav><br>  )<br>}<br>```<br><br>**Bottom Tabs (components/layout/BottomTabs.tsx):**<br>```typescript<br>export function BottomTabs() {<br>  const pathname = usePathname()<br>  <br>  return (<br>    <nav className="fixed bottom-0 left-0 right-0 border-t bg-background"<br>      <div className="flex justify-around items-center h-16"><br>        {navItems.map(item => (<br>          <Link<br>            key={item.href}<br>            href={item.href}<br>            className={cn(<br>              'flex flex-col items-center p-2',<br>              pathname === item.href && 'text-primary'<br>            )}<br>          ><br>            <item.icon className="w-6 h-6" /><br>            <span className="text-xs">{item.label}</span><br>          </Link><br>        ))}<br>        <QuickAddButton variant="mobile" /><br>      </div><br>    </nav><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Click Capture. Navigate to /capture. Capture nav item highlighted. Click Plan. Navigate to /plan. |
| **2** | **Test Logic** | **Given** on /plan,<br>**Then** Plan nav item has active class.<br>**When** Capture clicked,<br>**Then** navigates to /capture. |
| **3** | **Formal Tests** | Render nav. Click item. Verify navigation called. Verify active state styling. |

### D. Atomicity Validation

- **Yes.** Navigation only.

### E. Dependencies

- INF-001 (Next.js routing).

---

*End of Frontend Core Specifications*
