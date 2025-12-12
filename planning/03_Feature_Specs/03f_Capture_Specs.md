# Capture Feature Specifications

**Category:** CAP (Frontend Capture)
**Total Features:** 9
**Complexity:** 4 Easy, 5 Medium, 0 Hard

---

## CAP-001: Chat Message List

### A. User Story

> As a **User**, I want to **see my conversation history with the AI** so that I can follow the context of our discussion.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Display a scrollable list of chat messages between user and AI. User messages on right, AI on left. Support streaming messages that update in real-time. Auto-scroll to newest message. |
| **2** | **Logic Flow** | 1. Receive messages array as prop.<br>2. Render each message with role-based styling.<br>3. Handle streaming message (partial content).<br>4. Auto-scroll on new message.<br>5. Show typing indicator during AI response. |
| **3** | **Formal Interfaces** | **ChatMessageList Component (components/chat/ChatMessageList.tsx):**<br>```typescript<br>interface Message {<br>  id: string<br>  role: 'user' \| 'assistant'<br>  content: string<br>  createdAt: Date<br>  isStreaming?: boolean<br>}<br><br>interface ChatMessageListProps {<br>  messages: Message[]<br>  streamingContent?: string<br>  isLoading?: boolean<br>}<br><br>export function ChatMessageList({<br>  messages,<br>  streamingContent,<br>  isLoading<br>}: ChatMessageListProps) {<br>  const scrollRef = useRef<HTMLDivElement>(null)<br>  <br>  useEffect(() => {<br>    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })<br>  }, [messages, streamingContent])<br>  <br>  return (<br>    <div className="flex-1 overflow-y-auto p-4 space-y-4"><br>      {messages.map(message => (<br>        <ChatBubble<br>          key={message.id}<br>          message={message}<br>        /><br>      ))}<br>      <br>      {streamingContent && (<br>        <ChatBubble<br>          message={{<br>            id: 'streaming',<br>            role: 'assistant',<br>            content: streamingContent,<br>            createdAt: new Date(),<br>            isStreaming: true<br>          }}<br>        /><br>      )}<br>      <br>      {isLoading && !streamingContent && (<br>        <TypingIndicator /><br>      )}<br>      <br>      <div ref={scrollRef} /><br>    </div><br>  )<br>}<br>```<br><br>**ChatBubble Component:**<br>```typescript<br>function ChatBubble({ message }: { message: Message }) {<br>  const isUser = message.role === 'user'<br>  <br>  return (<br>    <div className={cn(<br>      'flex',<br>      isUser ? 'justify-end' : 'justify-start'<br>    )}><br>      <div className={cn(<br>        'max-w-[80%] rounded-lg px-4 py-2',<br>        isUser <br>          ? 'bg-primary text-primary-foreground' <br>          : 'bg-muted',<br>        message.isStreaming && 'animate-pulse'<br>      )}><br>        <p className="whitespace-pre-wrap">{message.content}</p><br>        {message.isStreaming && (<br>          <span className="inline-block w-2 h-4 bg-current animate-blink ml-1" /><br>        )}<br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send message. See it appear on right. AI responds. Response appears on left with streaming animation. Scroll follows new messages. |
| **2** | **Test Logic** | **Given** 3 messages (user, assistant, user),<br>**When** rendered,<br>**Then** user messages styled right, assistant styled left.<br>**When** streamingContent provided,<br>**Then** streaming bubble appears with cursor. |
| **3** | **Formal Tests** | Render with mock messages. Verify role-based styling. Pass streamingContent. Verify streaming indicator visible. |

### D. Atomicity Validation

- **Yes.** Message display only.

### E. Dependencies

- FE-003 (SSE handler for streaming).

---

## CAP-002: Chat Text Input

### A. User Story

> As a **User**, I want to **type messages to the AI** so that I can capture my thoughts and get help.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a text input field with send button. Support Enter to send, Shift+Enter for newline. Disable while AI is responding. Show character limit feedback. |
| **2** | **Logic Flow** | 1. Controlled textarea with value state.<br>2. Handle Enter key (send) vs Shift+Enter (newline).<br>3. Call onSend callback with content.<br>4. Clear input after send.<br>5. Disable during loading state. |
| **3** | **Formal Interfaces** | **ChatInput Component (components/chat/ChatInput.tsx):**<br>```typescript<br>interface ChatInputProps {<br>  onSend: (content: string) => void<br>  disabled?: boolean<br>  placeholder?: string<br>  maxLength?: number<br>}<br><br>export function ChatInput({<br>  onSend,<br>  disabled = false,<br>  placeholder = "What's on your mind?",<br>  maxLength = 2000<br>}: ChatInputProps) {<br>  const [value, setValue] = useState('')<br>  const textareaRef = useRef<HTMLTextAreaElement>(null)<br>  <br>  const handleKeyDown = (e: React.KeyboardEvent) => {<br>    if (e.key === 'Enter' && !e.shiftKey) {<br>      e.preventDefault()<br>      handleSend()<br>    }<br>  }<br>  <br>  const handleSend = () => {<br>    const trimmed = value.trim()<br>    if (trimmed && !disabled) {<br>      onSend(trimmed)<br>      setValue('')<br>      textareaRef.current?.focus()<br>    }<br>  }<br>  <br>  // Auto-resize textarea<br>  useEffect(() => {<br>    if (textareaRef.current) {<br>      textareaRef.current.style.height = 'auto'<br>      textareaRef.current.style.height = <br>        `${textareaRef.current.scrollHeight}px`<br>    }<br>  }, [value])<br>  <br>  return (<br>    <div className="border-t p-4 bg-background"><br>      <div className="flex gap-2 items-end"><br>        <textarea<br>          ref={textareaRef}<br>          value={value}<br>          onChange={(e) => setValue(e.target.value.slice(0, maxLength))}<br>          onKeyDown={handleKeyDown}<br>          placeholder={placeholder}<br>          disabled={disabled}<br>          rows={1}<br>          className={cn(<br>            'flex-1 resize-none rounded-lg border p-3',<br>            'focus:outline-none focus:ring-2 focus:ring-primary',<br>            'max-h-32 overflow-y-auto',<br>            disabled && 'opacity-50 cursor-not-allowed'<br>          )}<br>        /><br>        <button<br>          onClick={handleSend}<br>          disabled={disabled \|\| !value.trim()}<br>          className={cn(<br>            'p-3 rounded-lg bg-primary text-primary-foreground',<br>            'disabled:opacity-50 disabled:cursor-not-allowed'<br>          )}<br>          aria-label="Send message"<br>        ><br>          <Send className="w-5 h-5" /><br>        </button><br>      </div><br>      {value.length > maxLength * 0.9 && (<br>        <p className="text-xs text-muted-foreground mt-1"<br>          {value.length}/{maxLength}<br>        </p><br>      )}<br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Type message. Press Enter. onSend fires with content. Input clears. While disabled, cannot type or send. |
| **2** | **Test Logic** | **Given** user types "Hello",<br>**When** Enter pressed,<br>**Then** onSend called with "Hello".<br>**Then** input value is empty. |
| **3** | **Formal Tests** | Render input. Type text. Press Enter. Verify onSend called. Verify input cleared. Test disabled state. |

### D. Atomicity Validation

- **Yes.** Text input only.

### E. Dependencies

- None.

---

## CAP-003: Chat Voice Input

### A. User Story

> As a **User**, I want to **speak my thoughts instead of typing** so that I can capture ideas quickly and naturally.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Add voice recording button to chat input. Tap to start recording, tap again to stop. Show recording indicator. Send audio to transcription service. Insert transcribed text into input. |
| **2** | **Logic Flow** | 1. Check for microphone permission.<br>2. On tap, start MediaRecorder.<br>3. Show recording animation/time.<br>4. On stop, send blob to transcription API.<br>5. Display transcription in text input.<br>6. User can edit before sending. |
| **3** | **Formal Interfaces** | **VoiceInput Component (components/chat/VoiceInput.tsx):**<br>```typescript<br>interface VoiceInputProps {<br>  onTranscription: (text: string) => void<br>  disabled?: boolean<br>}<br><br>export function VoiceInput({<br>  onTranscription,<br>  disabled<br>}: VoiceInputProps) {<br>  const [isRecording, setIsRecording] = useState(false)<br>  const [isTranscribing, setIsTranscribing] = useState(false)<br>  const [duration, setDuration] = useState(0)<br>  const mediaRecorderRef = useRef<MediaRecorder \| null>(null)<br>  const chunksRef = useRef<Blob[]>([])<br>  <br>  const startRecording = async () => {<br>    try {<br>      const stream = await navigator.mediaDevices.getUserMedia({ <br>        audio: true <br>      })<br>      const mediaRecorder = new MediaRecorder(stream)<br>      mediaRecorderRef.current = mediaRecorder<br>      chunksRef.current = []<br>      <br>      mediaRecorder.ondataavailable = (e) => {<br>        chunksRef.current.push(e.data)<br>      }<br>      <br>      mediaRecorder.onstop = async () => {<br>        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })<br>        stream.getTracks().forEach(t => t.stop())<br>        await transcribe(blob)<br>      }<br>      <br>      mediaRecorder.start()<br>      setIsRecording(true)<br>    } catch (err) {<br>      toast.error('Microphone access denied')<br>    }<br>  }<br>  <br>  const stopRecording = () => {<br>    mediaRecorderRef.current?.stop()<br>    setIsRecording(false)<br>  }<br>  <br>  const transcribe = async (blob: Blob) => {<br>    setIsTranscribing(true)<br>    try {<br>      const formData = new FormData()<br>      formData.append('audio', blob)<br>      const response = await api.transcribe(formData)<br>      onTranscription(response.text)<br>    } catch (err) {<br>      toast.error('Transcription failed')<br>    } finally {<br>      setIsTranscribing(false)<br>    }<br>  }<br>  <br>  // Duration timer<br>  useEffect(() => {<br>    let interval: NodeJS.Timeout<br>    if (isRecording) {<br>      setDuration(0)<br>      interval = setInterval(() => setDuration(d => d + 1), 1000)<br>    }<br>    return () => clearInterval(interval)<br>  }, [isRecording])<br>  <br>  return (<br>    <button<br>      onClick={isRecording ? stopRecording : startRecording}<br>      disabled={disabled \|\| isTranscribing}<br>      className={cn(<br>        'p-3 rounded-full',<br>        isRecording ? 'bg-red-500 animate-pulse' : 'bg-muted',<br>        disabled && 'opacity-50'<br>      )}<br>      aria-label={isRecording ? 'Stop recording' : 'Start voice input'}<br>    ><br>      {isTranscribing ? (<br>        <Spinner size="sm" /><br>      ) : (<br>        <Mic className={cn('w-5 h-5', isRecording && 'text-white')} /><br>      )}<br>      {isRecording && (<br>        <span className="ml-2 text-sm text-white">{duration}s</span><br>      )}<br>    </button><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Tap mic. See recording indicator. Speak. Tap again. See transcription appear in input. |
| **2** | **Test Logic** | **Given** mic permission granted,<br>**When** mic button tapped,<br>**Then** isRecording true, button shows stop state.<br>**When** stopped,<br>**Then** transcription request sent.<br>**When** complete,<br>**Then** onTranscription called with text. |
| **3** | **Formal Tests** | Mock MediaRecorder and API. Start recording. Stop. Verify API called. Verify callback fired. |

### D. Atomicity Validation

- **Yes.** Voice recording and transcription only.

### E. Dependencies

- INT-003 (Deepgram client).
- INT-006 (Voice transcription flow).

---

## CAP-004: Ghost Card

### A. User Story

> As a **User**, I want to **see immediate visual feedback when I capture a thought** so that I know the system received it.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | When user sends a message, immediately show a "ghost" card representing the pending extraction. Ghost card pulses/shimmers while AI processes. Transforms into real action card when extraction completes. |
| **2** | **Logic Flow** | 1. User sends capture message.<br>2. Immediately render ghost card with raw text.<br>3. Apply shimmer animation.<br>4. When extraction returns, animate transition.<br>5. Replace with real ActionCard. |
| **3** | **Formal Interfaces** | **GhostCard Component (components/capture/GhostCard.tsx):**<br>```typescript<br>interface GhostCardProps {<br>  rawText: string<br>  status: 'extracting' \| 'extracted' \| 'error'<br>  extractedAction?: Action<br>  onConfirm?: (action: Action) => void<br>  onEdit?: (action: Action) => void<br>}<br><br>export function GhostCard({<br>  rawText,<br>  status,<br>  extractedAction,<br>  onConfirm,<br>  onEdit<br>}: GhostCardProps) {<br>  if (status === 'extracted' && extractedAction) {<br>    return (<br>      <motion.div<br>        initial={{ opacity: 0, scale: 0.95 }}<br>        animate={{ opacity: 1, scale: 1 }}<br>        className="relative"<br>      ><br>        <ActionCard action={extractedAction} /><br>        <div className="flex gap-2 mt-2"><br>          <button <br>            onClick={() => onConfirm?.(extractedAction)}<br>            className="text-sm text-primary"<br>          ><br>            Looks good<br>          </button><br>          <button <br>            onClick={() => onEdit?.(extractedAction)}<br>            className="text-sm text-muted-foreground"<br>          ><br>            Edit<br>          </button><br>        </div><br>      </motion.div><br>    )<br>  }<br>  <br>  if (status === 'error') {<br>    return (<br>      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4"><br>        <p className="text-sm text-destructive">Failed to process</p><br>        <p className="text-sm text-muted-foreground mt-1">"{rawText}"</p><br>      </div><br>    )<br>  }<br>  <br>  // Extracting state - shimmer<br>  return (<br>    <div className="rounded-lg border bg-card p-4 relative overflow-hidden"><br>      <div className="absolute inset-0 shimmer-animation" /><br>      <p className="text-muted-foreground text-sm relative z-10"><br>        Processing: "{rawText.slice(0, 50)}..."<br>      </p><br>    </div><br>  )<br>}<br>```<br><br>**Shimmer CSS:**<br>```css<br>@keyframes shimmer {<br>  0% { transform: translateX(-100%); }<br>  100% { transform: translateX(100%); }<br>}<br><br>.shimmer-animation {<br>  background: linear-gradient(<br>    90deg,<br>    transparent,<br>    rgba(255,255,255,0.2),<br>    transparent<br>  );<br>  animation: shimmer 1.5s infinite;<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send "Buy milk". See ghost card with shimmer. Extraction completes. See solid card with "Buy milk" title. Click "Looks good". Card confirmed. |
| **2** | **Test Logic** | **Given** status="extracting",<br>**Then** shimmer visible.<br>**When** status="extracted",<br>**Then** ActionCard visible with confirm button. |
| **3** | **Formal Tests** | Render in each status. Verify correct UI displayed. Click confirm. Verify callback. |

### D. Atomicity Validation

- **Yes.** Ghost card display only.

### E. Dependencies

- FE-006 (ActionCard component).
- AGT-016 (Extraction Orchestrator).

---

## CAP-005: Confidence Validation

### A. User Story

> As a **User**, I want to **confirm or correct AI extractions** when the system is uncertain so that my tasks are captured accurately.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | When extraction confidence is low (<0.7), show validation prompt. Display what the AI understood with option to confirm or edit. Highlight uncertain parts. |
| **2** | **Logic Flow** | 1. Receive extraction with confidence score.<br>2. If confidence >= 0.7, auto-confirm.<br>3. If confidence < 0.7, show validation UI.<br>4. Display AI interpretation with ambiguities.<br>5. User can confirm as-is or edit.<br>6. On confirm, save to database. |
| **3** | **Formal Interfaces** | **ConfidenceValidation Component (components/capture/ConfidenceValidation.tsx):**<br>```typescript<br>interface ConfidenceValidationProps {<br>  extraction: ExtractionResult<br>  onConfirm: (actions: Action[]) => void<br>  onEdit: (action: Action) => void<br>}<br><br>export function ConfidenceValidation({<br>  extraction,<br>  onConfirm,<br>  onEdit<br>}: ConfidenceValidationProps) {<br>  const { actions, confidence, ambiguities } = extraction<br>  <br>  return (<br>    <div className="bg-warning/10 border border-warning/50 rounded-lg p-4"><br>      <div className="flex items-center gap-2 mb-3"><br>        <AlertCircle className="w-5 h-5 text-warning" /><br>        <p className="font-medium">Did I get this right?</p><br>      </div><br>      <br>      <div className="space-y-3"><br>        {actions.map((action, i) => (<br>          <div key={i} className="bg-background rounded-lg p-3"><br>            <p className="font-medium">{action.title}</p><br>            {action.estimated_minutes && (<br>              <p className="text-sm text-muted-foreground"><br>                ~{action.estimated_minutes} min<br>              </p><br>            )}<br>          </div><br>        ))}<br>      </div><br>      <br>      {ambiguities.length > 0 && (<br>        <div className="mt-3 text-sm text-muted-foreground"><br>          <p>I wasn't sure about:</p><br>          <ul className="list-disc list-inside"><br>            {ambiguities.map((a, i) => (<br>              <li key={i}>{a}</li><br>            ))}<br>          </ul><br>        </div><br>      )}<br>      <br>      <div className="flex gap-2 mt-4"><br>        <button<br>          onClick={() => onConfirm(actions)}<br>          className="px-4 py-2 bg-primary text-primary-foreground rounded-md"<br>        ><br>          Yes, that's right<br>        </button><br>        <button<br>          onClick={() => onEdit(actions[0])}<br>          className="px-4 py-2 text-muted-foreground"<br>        ><br>          Let me fix it<br>        </button><br>      </div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Low confidence extraction shown. See "Did I get this right?" prompt. See extracted actions. Click "Yes" to confirm. Click "Let me fix it" to edit. |
| **2** | **Test Logic** | **Given** confidence=0.5,<br>**Then** validation prompt shown.<br>**When** "Yes" clicked,<br>**Then** onConfirm called with actions. |
| **3** | **Formal Tests** | Render with low confidence. Verify prompt visible. Click confirm. Verify callback. |

### D. Atomicity Validation

- **Yes.** Validation UI only.

### E. Dependencies

- AGT-016 (Extraction Orchestrator - provides confidence).
- CAP-006 (Correction flow for edit path).

---

## CAP-006: Correction Flow

### A. User Story

> As a **User**, I want to **edit extracted actions before saving** so that I can fix mistakes in the AI's interpretation.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Show edit form for action. Allow changing title, time estimate, and other fields. Save updates and close editor. |
| **2** | **Logic Flow** | 1. Receive action to edit.<br>2. Populate form with current values.<br>3. Allow edits to title, estimate, description.<br>4. On save, call onUpdate callback.<br>5. Close editor. |
| **3** | **Formal Interfaces** | **ActionEditForm Component (components/capture/ActionEditForm.tsx):**<br>```typescript<br>interface ActionEditFormProps {<br>  action: Action<br>  onSave: (updated: Partial<Action>) => void<br>  onCancel: () => void<br>}<br><br>export function ActionEditForm({<br>  action,<br>  onSave,<br>  onCancel<br>}: ActionEditFormProps) {<br>  const [title, setTitle] = useState(action.title)<br>  const [estimatedMinutes, setEstimatedMinutes] = useState(<br>    action.estimated_minutes ?? 15<br>  )<br>  const [description, setDescription] = useState(<br>    action.description ?? ''<br>  )<br>  <br>  const handleSubmit = (e: React.FormEvent) => {<br>    e.preventDefault()<br>    onSave({<br>      title: title.trim(),<br>      estimated_minutes: estimatedMinutes,<br>      description: description.trim() \|\| undefined<br>    })<br>  }<br>  <br>  return (<br>    <form onSubmit={handleSubmit} className="space-y-4"><br>      <div><br>        <label className="text-sm font-medium">What needs to be done?</label><br>        <input<br>          type="text"<br>          value={title}<br>          onChange={(e) => setTitle(e.target.value)}<br>          className="w-full mt-1 rounded-md border p-2"<br>          autoFocus<br>          required<br>        /><br>      </div><br>      <br>      <div><br>        <label className="text-sm font-medium">How long? (minutes)</label><br>        <input<br>          type="number"<br>          value={estimatedMinutes}<br>          onChange={(e) => setEstimatedMinutes(parseInt(e.target.value))}<br>          min={5}<br>          max={480}<br>          step={5}<br>          className="w-full mt-1 rounded-md border p-2"<br>        /><br>      </div><br>      <br>      <div><br>        <label className="text-sm font-medium">Any notes? (optional)</label><br>        <textarea<br>          value={description}<br>          onChange={(e) => setDescription(e.target.value)}<br>          className="w-full mt-1 rounded-md border p-2"<br>          rows={2}<br>        /><br>      </div><br>      <br>      <div className="flex gap-2 justify-end"><br>        <button<br>          type="button"<br>          onClick={onCancel}<br>          className="px-4 py-2 text-muted-foreground"<br>        ><br>          Cancel<br>        </button><br>        <button<br>          type="submit"<br>          className="px-4 py-2 bg-primary text-primary-foreground rounded-md"<br>        ><br>          Save<br>        </button><br>      </div><br>    </form><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open editor with action. Change title. Click Save. onSave called with updated values. |
| **2** | **Test Logic** | **Given** action with title "Byu milk",<br>**When** user changes to "Buy milk" and saves,<br>**Then** onSave called with title="Buy milk". |
| **3** | **Formal Tests** | Render with action. Change input values. Submit form. Verify onSave called with correct data. |

### D. Atomicity Validation

- **Yes.** Edit form only.

### E. Dependencies

- None.

---

## CAP-007: Voice Error Handling

### A. User Story

> As a **User**, I want to **see clear feedback when voice transcription fails** so that I know to try again or type instead.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | When transcription fails, show error message. Offer retry button and fallback to text input. Log error for debugging. |
| **2** | **Logic Flow** | 1. Detect transcription failure.<br>2. Show error toast or inline message.<br>3. Offer "Try again" button.<br>4. Suggest typing as alternative.<br>5. Log error details. |
| **3** | **Formal Interfaces** | **VoiceErrorHandler (in VoiceInput component):**<br>```typescript<br>interface VoiceErrorState {<br>  hasError: boolean<br>  errorType: 'permission' \| 'transcription' \| 'network' \| null<br>  message: string<br>}<br><br>// Inside VoiceInput component<br>const [error, setError] = useState<VoiceErrorState>({<br>  hasError: false,<br>  errorType: null,<br>  message: ''<br>})<br><br>const handleError = (type: VoiceErrorState['errorType'], err: Error) => {<br>  const messages = {<br>    permission: 'Microphone access denied. Please enable in settings.',<br>    transcription: "Couldn't understand that. Try speaking more clearly.",<br>    network: 'Connection issue. Check your internet and try again.'<br>  }<br>  <br>  setError({<br>    hasError: true,<br>    errorType: type,<br>    message: messages[type!]<br>  })<br>  <br>  // Log for debugging<br>  console.error('Voice error:', type, err)<br>}<br><br>// Error display<br>{error.hasError && (<br>  <div className="flex items-center gap-2 p-2 bg-destructive/10 rounded text-sm"><br>    <AlertCircle className="w-4 h-4 text-destructive" /><br>    <span>{error.message}</span><br>    {error.errorType !== 'permission' && (<br>      <button<br>        onClick={() => {<br>          setError({ hasError: false, errorType: null, message: '' })<br>          startRecording()<br>        }}<br>        className="text-primary underline"<br>      ><br>        Try again<br>      </button><br>    )}<br>  </div><br>)}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Recording fails. See error message. Click "Try again". Recording restarts. Permission denied. See permission-specific message. |
| **2** | **Test Logic** | **Given** transcription API fails,<br>**Then** error message shown with retry button.<br>**When** retry clicked,<br>**Then** recording restarts. |
| **3** | **Formal Tests** | Mock API to fail. Verify error displayed. Click retry. Verify recording restarted. |

### D. Atomicity Validation

- **Yes.** Error handling only.

### E. Dependencies

- CAP-003 (Voice input component).

---

## CAP-008: Quick Capture Overlay

### A. User Story

> As a **User**, I want to **capture quick thoughts during focus mode** without losing focus so that stray ideas don't distract me.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Show minimal overlay for capturing thoughts during focus. Single text input, no distractions. Saves to canvas/inbox, doesn't interrupt flow. Dismisses quickly. |
| **2** | **Logic Flow** | 1. Button in focus mode opens overlay.<br>2. Overlay slides in from corner.<br>3. Simple text input only.<br>4. On submit, save thought to inbox.<br>5. Show brief confirmation.<br>6. Auto-dismiss after save. |
| **3** | **Formal Interfaces** | **QuickCaptureOverlay Component (components/capture/QuickCaptureOverlay.tsx):**<br>```typescript<br>interface QuickCaptureOverlayProps {<br>  isOpen: boolean<br>  onClose: () => void<br>  onCapture: (text: string) => Promise<void><br>}<br><br>export function QuickCaptureOverlay({<br>  isOpen,<br>  onClose,<br>  onCapture<br>}: QuickCaptureOverlayProps) {<br>  const [value, setValue] = useState('')<br>  const [status, setStatus] = useState<'idle' \| 'saving' \| 'saved'>('idle')<br>  const inputRef = useRef<HTMLInputElement>(null)<br>  <br>  useEffect(() => {<br>    if (isOpen) {<br>      inputRef.current?.focus()<br>    }<br>  }, [isOpen])<br>  <br>  const handleSubmit = async (e: React.FormEvent) => {<br>    e.preventDefault()<br>    if (!value.trim()) return<br>    <br>    setStatus('saving')<br>    await onCapture(value.trim())<br>    setStatus('saved')<br>    setValue('')<br>    <br>    // Auto-close after brief confirmation<br>    setTimeout(() => {<br>      setStatus('idle')<br>      onClose()<br>    }, 1000)<br>  }<br>  <br>  if (!isOpen) return null<br>  <br>  return (<br>    <div className="fixed top-4 right-4 z-50"><br>      <motion.div<br>        initial={{ opacity: 0, x: 20 }}<br>        animate={{ opacity: 1, x: 0 }}<br>        exit={{ opacity: 0, x: 20 }}<br>        className="bg-background border rounded-lg shadow-lg p-4 w-80"<br>      ><br>        {status === 'saved' ? (<br>          <div className="flex items-center gap-2 text-green-600"><br>            <Check className="w-5 h-5" /><br>            <span>Saved to inbox</span><br>          </div><br>        ) : (<br>          <form onSubmit={handleSubmit}><br>            <label className="text-sm font-medium">Quick thought:</label><br>            <input<br>              ref={inputRef}<br>              type="text"<br>              value={value}<br>              onChange={(e) => setValue(e.target.value)}<br>              placeholder="What's on your mind?"<br>              className="w-full mt-2 rounded-md border p-2"<br>              disabled={status === 'saving'}<br>            /><br>            <div className="flex justify-end gap-2 mt-3"><br>              <button<br>                type="button"<br>                onClick={onClose}<br>                className="text-sm text-muted-foreground"<br>              ><br>                Cancel<br>              </button><br>              <button<br>                type="submit"<br>                disabled={!value.trim() \|\| status === 'saving'}<br>                className="text-sm px-3 py-1 bg-primary text-primary-foreground rounded"<br>              ><br>                {status === 'saving' ? 'Saving...' : 'Save'}<br>              </button><br>            </div><br>          </form><br>        )}<br>      </motion.div><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | In focus mode, click capture button. Overlay appears. Type thought. Press Enter. See "Saved" confirmation. Overlay closes. |
| **2** | **Test Logic** | **Given** overlay open,<br>**When** user types "Remember to call mom" and submits,<br>**Then** onCapture called with text.<br>**Then** shows "Saved" briefly.<br>**Then** closes. |
| **3** | **Formal Tests** | Open overlay. Type and submit. Verify onCapture called. Verify saved state shown. Verify auto-close. |

### D. Atomicity Validation

- **Yes.** Quick capture UI only.

### E. Dependencies

- EXE-001 (Focus mode container).

---

## CAP-009: Capture Page Container

### A. User Story

> As a **User**, I want to **have a unified capture experience** so that my text and voice inputs flow seamlessly through extraction and validation.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Page-level container that orchestrates all capture components. Manages conversation state, extraction status, and validation flow. Coordinates CAP-001 through CAP-008. |
| **2** | **Logic Flow** | 1. Render message list (CAP-001) and input (CAP-002/003).<br>2. On send, show ghost card (CAP-004).<br>3. Call AGT-016 for extraction.<br>4. If confidence >= 0.7, auto-confirm and save.<br>5. If confidence < 0.7, show validation (CAP-005).<br>6. On edit, show correction flow (CAP-006).<br>7. On confirm, save to database and update list. |
| **3** | **Formal Interfaces** | **CapturePage Component (app/capture/page.tsx):**<br>```typescript<br>interface CapturePageState {<br>  messages: Message[]<br>  pendingExtractions: Map<string, ExtractionStatus><br>  validationQueue: LowConfidenceAction[]<br>}<br><br>export function CapturePage() {<br>  const [state, dispatch] = useReducer(captureReducer, initialState)<br>  const { mutate: extract } = useExtraction()<br>  <br>  const handleSend = async (text: string) => {<br>    const messageId = addMessage(text)<br>    dispatch({ type: 'START_EXTRACTION', messageId })<br>    <br>    const result = await extract(text)<br>    <br>    if (result.confidence >= 0.7) {<br>      dispatch({ type: 'AUTO_CONFIRM', messageId, action: result.action })<br>    } else {<br>      dispatch({ type: 'NEEDS_VALIDATION', messageId, action: result.action })<br>    }<br>  }<br>  <br>  return (<br>    <div className="flex flex-col h-full"><br>      <ChatMessageList messages={state.messages} /><br>      {state.pendingExtractions.size > 0 && <GhostCard />}<br>      {state.validationQueue.length > 0 && (<br>        <ConfidenceValidation <br>          action={state.validationQueue[0]}<br>          onConfirm={handleConfirm}<br>          onEdit={handleEdit}<br>        /><br>      )}<br>      <ChatTextInput onSend={handleSend} /><br>    </div><br>  )<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Type message. See ghost card. Extraction completes. If high confidence, action saved. If low confidence, validation appears. Edit and confirm. Action saved. |
| **2** | **Test Logic** | **Given** text input,<br>**When** sent,<br>**Then** ghost card appears.<br>**When** extraction returns >= 0.7,<br>**Then** action auto-saved.<br>**When** extraction returns < 0.7,<br>**Then** validation shown. |
| **3** | **Formal Tests** | Mock AGT-016. Test high confidence path. Test low confidence path. Test edit flow. Verify final save. |

### D. Atomicity Validation

- **Yes.** Page orchestration only. Individual components handle their own rendering/logic.

### E. Dependencies

- CAP-001 (Chat Message List).
- CAP-002 (Chat Text Input).
- CAP-003 (Chat Voice Input).
- CAP-004 (Ghost Card).
- CAP-005 (Confidence Validation).
- CAP-006 (Correction Flow).
- CAP-007 (Voice Error Handling).
- CAP-008 (Quick Capture Overlay).
- FE-001 (API Client).
- AGT-016 (Extraction Orchestrator).

### F. Complexity

**Medium** - State machine coordination, multiple child components.

---

*End of Capture Specifications*
