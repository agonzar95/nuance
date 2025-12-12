# Agentic Feature Specifications

**Category:** AGT (Agentic)
**Total Features:** 16
**Complexity:** 4 Easy, 7 Medium, 5 Hard

---

## AGT-001: Orchestrator Setup

### A. User Story

> As a **Developer**, I want to **set up the API orchestrator with routing and middleware** so that all AI requests flow through a consistent pipeline.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create the main FastAPI router structure that handles all AI-related endpoints. Set up middleware for authentication, logging, and error handling. Configure dependency injection for services. |
| **2** | **Logic Flow** | 1. Create main router at `/api/ai/`.<br>2. Add auth middleware to validate JWT from Supabase.<br>3. Add request ID middleware for tracing.<br>4. Register sub-routers: `/chat`, `/extract`, `/transcribe`.<br>5. Inject dependencies: Claude client, Deepgram client, DB. |
| **3** | **Formal Interfaces** | **Router Structure (app/routers/ai.py):**<br>```python<br>from fastapi import APIRouter, Depends<br>from app.auth import get_current_user<br>from app.services.extraction import ExtractionService<br><br>router = APIRouter(prefix="/api/ai", tags=["ai"])<br><br>@router.post("/chat")<br>async def chat(<br>    request: ChatRequest,<br>    user: User = Depends(get_current_user),<br>    service: ChatService = Depends(get_chat_service)<br>):<br>    return await service.process(request, user)<br><br>@router.post("/extract")<br>async def extract(<br>    request: ExtractRequest,<br>    user: User = Depends(get_current_user),<br>    service: ExtractionService = Depends(get_extraction_service)<br>):<br>    return await service.extract(request.text, user)<br>```<br><br>**Auth Dependency:**<br>```python<br>async def get_current_user(authorization: str = Header()) -> User:<br>    token = authorization.replace("Bearer ", "")<br>    user = await verify_supabase_jwt(token)<br>    return user<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Call /api/ai/extract without auth token. Get 401. Call with valid token. Get successful response or proper error. |
| **2** | **Test Logic** | **Given** no Authorization header,<br>**When** POST /api/ai/extract,<br>**Then** 401 Unauthorized.<br>**Given** valid token,<br>**Then** proceeds to handler. |
| **3** | **Formal Tests** | `client.post("/api/ai/extract", headers={})` → 401. `client.post("/api/ai/extract", headers={"Authorization": "Bearer valid"})` → 200 or 400 (not 401). |

### D. Atomicity Validation

- **Yes.** Router and middleware setup only.

### E. Dependencies

- INF-002 (FastAPI project).
- INF-008 (Error middleware).
- INT-001 (Supabase for auth verification).

---

## AGT-002: Request Router

### A. User Story

> As a **System**, I want to **route user messages to the appropriate handler** so that capture requests go to extraction and coaching requests go to conversation.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a router service that examines the classified intent and dispatches to the correct handler. Support intents: CAPTURE, COACHING, COMMAND. |
| **2** | **Logic Flow** | 1. Receive classified intent from AGT-013.<br>2. Switch on intent type.<br>3. CAPTURE → ExtractionService.<br>4. COACHING → CoachingService.<br>5. COMMAND → CommandHandler (for /start, /help).<br>6. Return handler response. |
| **3** | **Formal Interfaces** | **Router Service (app/services/intent_router.py):**<br>```python<br>from enum import Enum<br><br>class Intent(str, Enum):<br>    CAPTURE = "capture"<br>    COACHING = "coaching"<br>    COMMAND = "command"<br><br>class IntentRouter:<br>    def __init__(<br>        self,<br>        extraction: ExtractionService,<br>        coaching: CoachingService,<br>        command: CommandHandler<br>    ):<br>        self.handlers = {<br>            Intent.CAPTURE: extraction.process,<br>            Intent.COACHING: coaching.process,<br>            Intent.COMMAND: command.process<br>        }<br>    <br>    async def route(<br>        self,<br>        intent: Intent,<br>        text: str,<br>        user: User,<br>        context: dict | None = None<br>    ) -> RouterResponse:<br>        handler = self.handlers[intent]<br>        return await handler(text, user, context)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send "Buy milk" (CAPTURE intent). Extraction is called. Send "I feel stuck" (COACHING intent). Coaching is called. |
| **2** | **Test Logic** | **Given** intent=CAPTURE,<br>**When** route() is called,<br>**Then** extraction.process was invoked.<br>**Given** intent=COACHING,<br>**Then** coaching.process was invoked. |
| **3** | **Formal Tests** | Mock all handlers. Call route with each intent. Assert correct handler was called with correct args. |

### D. Atomicity Validation

- **Yes.** Dispatch logic only.

### E. Dependencies

- AGT-001 (Orchestrator Setup).
- AGT-007 (Model Abstraction).
- AGT-013 (Intent Classifier - provides intent).
- AGT-016 (Extraction Orchestrator - for CAPTURE).
- AGT-014 (Coaching Handler - for COACHING).

**Note:** This feature should be built LAST in Phase 4 because it routes to all handlers.

---

## AGT-003: Circuit Breakers

### A. User Story

> As a **System**, I want to **fail fast when external services are down** so that users get quick feedback instead of hanging.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Implement circuit breaker pattern for Claude and Deepgram APIs. After 3 consecutive failures, open the circuit for 60 seconds. During open state, return immediate error. After cooldown, allow one test request. |
| **2** | **Logic Flow** | 1. Wrap API calls in circuit breaker.<br>2. On success: reset failure count.<br>3. On failure: increment count.<br>4. If failures >= threshold: open circuit.<br>5. In open state: reject immediately.<br>6. After cooldown: allow one request (half-open).<br>7. If test succeeds: close circuit. If fails: reopen. |
| **3** | **Formal Interfaces** | **Circuit Breaker (app/utils/circuit_breaker.py):**<br>```python<br>from datetime import datetime, timedelta<br>from enum import Enum<br><br>class CircuitState(Enum):<br>    CLOSED = "closed"<br>    OPEN = "open"<br>    HALF_OPEN = "half_open"<br><br>class CircuitBreaker:<br>    def __init__(<br>        self,<br>        name: str,<br>        failure_threshold: int = 3,<br>        cooldown_seconds: int = 60<br>    ):<br>        self.name = name<br>        self.failure_threshold = failure_threshold<br>        self.cooldown = timedelta(seconds=cooldown_seconds)<br>        self.state = CircuitState.CLOSED<br>        self.failures = 0<br>        self.last_failure: datetime | None = None<br>    <br>    async def call[T](self, func: Callable[[], Awaitable[T]]) -> T:<br>        if self.state == CircuitState.OPEN:<br>            if datetime.now() - self.last_failure > self.cooldown:<br>                self.state = CircuitState.HALF_OPEN<br>            else:<br>                raise CircuitOpenError(f"{self.name} circuit is open")<br>        <br>        try:<br>            result = await func()<br>            self._on_success()<br>            return result<br>        except Exception as e:<br>            self._on_failure()<br>            raise<br>    <br>    def _on_success(self):<br>        self.failures = 0<br>        self.state = CircuitState.CLOSED<br>    <br>    def _on_failure(self):<br>        self.failures += 1<br>        self.last_failure = datetime.now()<br>        if self.failures >= self.failure_threshold:<br>            self.state = CircuitState.OPEN<br>```<br><br>**Usage:**<br>```python<br>claude_circuit = CircuitBreaker("claude")<br><br>async def call_claude(messages):<br>    return await claude_circuit.call(<br>        lambda: claude_client.chat(messages)<br>    )<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Cause 3 API failures. 4th request immediately fails with "circuit open" error. Wait 60 seconds. Next request is attempted. |
| **2** | **Test Logic** | **Given** 3 consecutive failures,<br>**When** 4th call is made,<br>**Then** raises CircuitOpenError immediately.<br>**After** cooldown,<br>**Then** call is attempted. |
| **3** | **Formal Tests** | Mock failing function. Call 3 times. Assert 4th raises CircuitOpenError. Advance time. Assert 5th calls function. |

### D. Atomicity Validation

- **Yes.** Pattern implementation only.

### E. Dependencies

- INF-002 (FastAPI project for integration).

---

## AGT-004: Rate Limiting

### A. User Story

> As a **System**, I want to **limit API requests per user** so that no single user can exhaust resources or run up costs.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Implement per-user rate limiting for AI endpoints. Allow 60 requests per minute, 500 per day. Return 429 Too Many Requests when exceeded with retry-after header. |
| **2** | **Logic Flow** | 1. On each request, get user ID.<br>2. Check minute counter in Redis/memory.<br>3. Check daily counter.<br>4. If either exceeded: return 429.<br>5. Otherwise: increment counters, proceed.<br>6. Counters reset on window expiry. |
| **3** | **Formal Interfaces** | **Rate Limiter (app/utils/rate_limiter.py):**<br>```python<br>from datetime import datetime<br>from collections import defaultdict<br><br>class RateLimiter:<br>    def __init__(<br>        self,<br>        requests_per_minute: int = 60,<br>        requests_per_day: int = 500<br>    ):<br>        self.rpm = requests_per_minute<br>        self.rpd = requests_per_day<br>        self.minute_counts: dict[str, list[datetime]] = defaultdict(list)<br>        self.day_counts: dict[str, int] = defaultdict(int)<br>        self.day_reset: dict[str, datetime] = {}<br>    <br>    def check(self, user_id: str) -> tuple[bool, int | None]:<br>        """Returns (allowed, retry_after_seconds)."""<br>        now = datetime.now()<br>        <br>        # Clean old minute entries<br>        minute_ago = now - timedelta(minutes=1)<br>        self.minute_counts[user_id] = [<br>            t for t in self.minute_counts[user_id] if t > minute_ago<br>        ]<br>        <br>        # Check minute limit<br>        if len(self.minute_counts[user_id]) >= self.rpm:<br>            oldest = min(self.minute_counts[user_id])<br>            retry = 60 - (now - oldest).seconds<br>            return False, retry<br>        <br>        # Check daily limit<br>        if self.day_counts[user_id] >= self.rpd:<br>            return False, self._seconds_until_midnight()<br>        <br>        # Record request<br>        self.minute_counts[user_id].append(now)<br>        self.day_counts[user_id] += 1<br>        return True, None<br>```<br><br>**Middleware:**<br>```python<br>@app.middleware("http")<br>async def rate_limit_middleware(request: Request, call_next):<br>    if request.url.path.startswith("/api/ai/"):<br>        user_id = get_user_id_from_request(request)<br>        allowed, retry_after = rate_limiter.check(user_id)<br>        if not allowed:<br>            return JSONResponse(<br>                status_code=429,<br>                content={"error": "Rate limit exceeded"},<br>                headers={"Retry-After": str(retry_after)}<br>            )<br>    return await call_next(request)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send 61 requests in one minute. 61st returns 429 with Retry-After header. Wait, retry, succeeds. |
| **2** | **Test Logic** | **Given** 60 requests made in last minute,<br>**When** 61st request is made,<br>**Then** returns 429 with Retry-After > 0. |
| **3** | **Formal Tests** | Loop 60 requests, assert all 200. Request 61, assert 429. Check Retry-After header exists. |

### D. Atomicity Validation

- **Yes.** Rate limiting logic only.

### E. Dependencies

- AGT-001 (Orchestrator for middleware integration).

---

## AGT-005: Token Budgeting

### A. User Story

> As a **System**, I want to **track and limit token usage** so that costs are predictable and users don't accidentally burn through credits.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Track input and output tokens per API call. Maintain daily token budget per user (100K tokens). Warn at 80%, block at 100%. Store usage in database for analytics. |
| **2** | **Logic Flow** | 1. Before AI call: estimate input tokens.<br>2. Check if user has budget remaining.<br>3. If < 20% remaining: add warning to response.<br>4. If exhausted: return error, no AI call.<br>5. After call: record actual usage.<br>6. Reset daily at midnight user's timezone. |
| **3** | **Formal Interfaces** | **Token Tracker (app/services/token_budget.py):**<br>```python<br>from dataclasses import dataclass<br><br>@dataclass<br>class TokenUsage:<br>    input_tokens: int<br>    output_tokens: int<br>    <br>    @property<br>    def total(self) -> int:<br>        return self.input_tokens + self.output_tokens<br><br>class TokenBudgetService:<br>    DAILY_LIMIT = 100_000<br>    WARNING_THRESHOLD = 0.8<br>    <br>    async def check_budget(self, user_id: str) -> tuple[bool, float]:<br>        """Returns (has_budget, percentage_used)."""<br>        usage = await self._get_today_usage(user_id)<br>        percentage = usage / self.DAILY_LIMIT<br>        return percentage < 1.0, percentage<br>    <br>    async def record_usage(<br>        self,<br>        user_id: str,<br>        usage: TokenUsage,<br>        endpoint: str<br>    ) -> None:<br>        await supabase.table('token_usage').insert({<br>            'user_id': user_id,<br>            'input_tokens': usage.input_tokens,<br>            'output_tokens': usage.output_tokens,<br>            'endpoint': endpoint,<br>            'created_at': datetime.now(UTC).isoformat()<br>        }).execute()<br>    <br>    async def _get_today_usage(self, user_id: str) -> int:<br>        today = await self._get_user_today(user_id)<br>        result = await supabase.table('token_usage').select(<br>            'input_tokens, output_tokens'<br>        ).eq('user_id', user_id).gte(<br>            'created_at', today.isoformat()<br>        ).execute()<br>        return sum(r['input_tokens'] + r['output_tokens'] for r in result.data)<br>```<br><br>**Usage Table:**<br>```sql<br>CREATE TABLE token_usage (<br>  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),<br>  user_id UUID REFERENCES auth.users NOT NULL,<br>  input_tokens INT NOT NULL,<br>  output_tokens INT NOT NULL,<br>  endpoint TEXT,<br>  created_at TIMESTAMPTZ DEFAULT NOW()<br>);<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Use 80K tokens. Next response includes warning. Use 100K total. Next request is blocked with error. Next day, budget resets. |
| **2** | **Test Logic** | **Given** 80K tokens used today,<br>**When** check_budget(),<br>**Then** returns (True, 0.8).<br>**Given** 100K used,<br>**Then** returns (False, 1.0). |
| **3** | **Formal Tests** | Insert token_usage rows. Call check_budget. Assert correct percentage. Assert blocking at 100%. |

### D. Atomicity Validation

- **Yes.** Budget tracking only.

### E. Dependencies

- SUB-001 (Database for usage storage).
- INT-002 (Claude client for token counts).

---

## AGT-006: SSE Streaming

### A. User Story

> As a **User**, I want to **see AI responses appear word-by-word** so that I get immediate feedback and the app feels responsive.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Implement Server-Sent Events (SSE) endpoint that streams Claude responses. Send chunks as they arrive. Include special events for extraction results. Handle connection drops gracefully. |
| **2** | **Logic Flow** | 1. Client connects to SSE endpoint.<br>2. Backend calls Claude with stream=True.<br>3. As chunks arrive, send as SSE events.<br>4. On completion, send done event.<br>5. If extraction, send extracted data as final event.<br>6. Close connection. |
| **3** | **Formal Interfaces** | **SSE Endpoint (app/routers/ai.py):**<br>```python<br>from fastapi.responses import StreamingResponse<br>from sse_starlette.sse import EventSourceResponse<br><br>@router.post("/chat/stream")<br>async def chat_stream(<br>    request: ChatRequest,<br>    user: User = Depends(get_current_user)<br>):<br>    async def event_generator():<br>        try:<br>            async for chunk in claude.chat_stream(request.messages):<br>                yield {<br>                    "event": "message",<br>                    "data": json.dumps({"content": chunk})<br>                }<br>            yield {"event": "done", "data": "{}"}<br>        except Exception as e:<br>            yield {<br>                "event": "error",<br>                "data": json.dumps({"error": str(e)})<br>            }<br>    <br>    return EventSourceResponse(event_generator())<br>```<br><br>**Event Types:**<br>```typescript<br>type SSEEvent = <br>  | { event: "message"; data: { content: string } }<br>  | { event: "extraction"; data: { actions: Action[] } }<br>  | { event: "done"; data: {} }<br>  | { event: "error"; data: { error: string } }<br>```<br><br>**Frontend Handler:**<br>```typescript<br>const eventSource = new EventSource('/api/ai/chat/stream')<br>eventSource.addEventListener('message', (e) => {<br>  const { content } = JSON.parse(e.data)<br>  appendToMessage(content)<br>})<br>eventSource.addEventListener('done', () => {<br>  eventSource.close()<br>})<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Start chat request. See text appear incrementally. Connection closes after "done" event. Network error shows error event. |
| **2** | **Test Logic** | **Given** streaming response,<br>**When** receiving events,<br>**Then** multiple "message" events arrive.<br>**Then** final "done" event arrives. |
| **3** | **Formal Tests** | Call streaming endpoint. Collect all events. Assert >= 2 message events. Assert done event is last. |

### D. Atomicity Validation

- **Yes.** Streaming infrastructure only.

### E. Dependencies

- INT-002 (Claude client with streaming).
- AGT-001 (Orchestrator for endpoint).

---

## AGT-007: Model Abstraction

### A. User Story

> As a **Developer**, I want to **abstract the AI provider** so that I can switch models or providers without changing application code.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create an interface for AI completions that different providers implement. Support Claude now with ability to add others. Standardize request/response format. |
| **2** | **Logic Flow** | 1. Define abstract AIProvider interface.<br>2. Implement ClaudeProvider.<br>3. Factory function selects provider by config.<br>4. All services use abstract interface.<br>5. Provider details hidden from consumers. |
| **3** | **Formal Interfaces** | **Abstract Provider (app/ai/base.py):**<br>```python<br>from abc import ABC, abstractmethod<br>from typing import AsyncIterator<br>from pydantic import BaseModel<br><br>class Message(BaseModel):<br>    role: str  # "user" | "assistant" | "system"<br>    content: str<br><br>class CompletionResponse(BaseModel):<br>    content: str<br>    input_tokens: int<br>    output_tokens: int<br><br>class AIProvider(ABC):<br>    @abstractmethod<br>    async def complete(<br>        self,<br>        messages: list[Message],<br>        system: str | None = None,<br>        max_tokens: int = 1024<br>    ) -> CompletionResponse: ...<br>    <br>    @abstractmethod<br>    async def stream(<br>        self,<br>        messages: list[Message],<br>        system: str | None = None<br>    ) -> AsyncIterator[str]: ...<br>    <br>    @abstractmethod<br>    async def extract[T: BaseModel](<br>        self,<br>        text: str,<br>        schema: type[T],<br>        system: str<br>    ) -> T: ...<br>```<br><br>**Claude Implementation (app/ai/claude.py):**<br>```python<br>class ClaudeProvider(AIProvider):<br>    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):<br>        self.client = Anthropic(api_key=api_key)<br>        self.model = model<br>    <br>    async def complete(self, messages, system=None, max_tokens=1024):<br>        response = await self.client.messages.create(<br>            model=self.model,<br>            messages=messages,<br>            system=system,<br>            max_tokens=max_tokens<br>        )<br>        return CompletionResponse(<br>            content=response.content[0].text,<br>            input_tokens=response.usage.input_tokens,<br>            output_tokens=response.usage.output_tokens<br>        )<br>```<br><br>**Factory:**<br>```python<br>def get_ai_provider() -> AIProvider:<br>    return ClaudeProvider(settings.anthropic_api_key)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Call provider.complete(). Get response with content and token counts. Same interface works regardless of underlying model. |
| **2** | **Test Logic** | **Given** ClaudeProvider instance,<br>**When** complete() is called,<br>**Then** returns CompletionResponse with all fields. |
| **3** | **Formal Tests** | Mock Anthropic client. Call complete(). Assert response type is CompletionResponse. Assert tokens are integers. |

### D. Atomicity Validation

- **Yes.** Interface and implementation only.

### E. Dependencies

- INT-002 (Claude API client).

---

## AGT-008: Extract: Actions

### A. User Story

> As a **User**, I want to **speak naturally about my tasks** and have them automatically converted into structured actions.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Parse natural language input to extract one or more actions. Each action has title, estimated time, and raw input reference. Handle multiple tasks in one utterance. Handle ambiguous input gracefully. |
| **2** | **Logic Flow** | 1. Receive raw text input.<br>2. Call Claude with extraction prompt.<br>3. Request structured JSON output.<br>4. Parse response into Action objects.<br>5. Validate each action has required fields.<br>6. Return list of extracted actions. |
| **3** | **Formal Interfaces** | **Extraction Service (app/services/extraction.py):**<br>```python<br>from pydantic import BaseModel, Field<br><br>class ExtractedAction(BaseModel):<br>    title: str = Field(..., description="Clear, actionable task title")<br>    estimated_minutes: int = Field(15, ge=5, le=480)<br>    raw_segment: str = Field(..., description="Original text this was extracted from")<br><br>class ExtractionResult(BaseModel):<br>    actions: list[ExtractedAction]<br>    confidence: float = Field(..., ge=0, le=1)<br><br>EXTRACTION_PROMPT = """<br>You are an executive function assistant helping extract actionable tasks.<br><br>Given the user's input, identify distinct tasks and extract them as structured actions.<br><br>Rules:<br>- Each task should be concrete and actionable<br>- Estimate time in minutes (round to 15-minute increments)<br>- If input is vague, create a reasonable interpretation<br>- Multiple tasks in one sentence should be split<br>- Preserve the user's language where possible<br><br>Examples:<br>"I need to call mom and buy groceries" → 2 actions<br>"That big report thing" → 1 action: "Work on report"<br>"""<br><br>class ExtractionService:<br>    def __init__(self, ai: AIProvider):<br>        self.ai = ai<br>    <br>    async def extract(self, text: str) -> ExtractionResult:<br>        result = await self.ai.extract(<br>            text=text,<br>            schema=ExtractionResult,<br>            system=EXTRACTION_PROMPT<br>        )<br>        return result<br>```<br><br>**Test Cases:**<br>```python<br>TEST_CASES = [<br>    ("Buy milk", [{"title": "Buy milk", "estimated_minutes": 15}]),<br>    ("Call mom and email boss", [<br>        {"title": "Call mom", "estimated_minutes": 15},<br>        {"title": "Email boss", "estimated_minutes": 15}<br>    ]),<br>    ("Work on that big project thing", [<br>        {"title": "Work on project", "estimated_minutes": 60}<br>    ])<br>]<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Say "Buy milk and call mom." Get 2 actions extracted. Each has title and time estimate. |
| **2** | **Test Logic** | **Given** "Buy milk and walk dog",<br>**When** extract() is called,<br>**Then** returns 2 actions.<br>**Then** each has title and estimated_minutes. |
| **3** | **Formal Tests** | Call with test cases. Assert action count. Assert titles contain key words. Assert times are reasonable (15-480). |

### D. Atomicity Validation

- **Yes.** Core extraction logic only.

### E. Dependencies

- AGT-007 (AI provider interface).
- AGT-015 (Prompt versioning for EXTRACTION_PROMPT).

---

## AGT-009: Extract: Avoidance Weight

### A. User Story

> As a **System**, I want to **detect emotional resistance in tasks** so that I can highlight hard wins and offer extra support.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Analyze task descriptions for signals of emotional difficulty: dread words ("ugh", "hate"), anxiety markers ("need to finally"), avoidance language ("been putting off"). Score from 1 (easy) to 5 (high avoidance). |
| **2** | **Logic Flow** | 1. Receive action title and raw input context.<br>2. Call Claude with avoidance detection prompt.<br>3. Analyze linguistic markers.<br>4. Return score 1-5.<br>5. Weight 4-5 triggers special handling in UI. |
| **3** | **Formal Interfaces** | **Avoidance Detector (in extraction.py):**<br>```python<br>class AvoidanceAnalysis(BaseModel):<br>    weight: int = Field(..., ge=1, le=5)<br>    signals: list[str] = Field(default_factory=list)<br>    reasoning: str<br><br>AVOIDANCE_PROMPT = """<br>Analyze the emotional resistance in this task description.<br><br>Score from 1-5:<br>1 = Neutral/easy task, no resistance signals<br>2 = Mild reluctance or minor annoyance<br>3 = Moderate avoidance, some emotional weight<br>4 = Significant resistance, dread language<br>5 = High avoidance, fear or strong negative emotion<br><br>Signals to look for:<br>- Explicit dread: "ugh", "hate", "dreading"<br>- Anxiety markers: "finally", "have to", "should have"<br>- Avoidance history: "been putting off", "keep forgetting"<br>- Emotional load: "scary", "overwhelming", "huge"<br>- Minimization: "just need to", "only have to" (often masks difficulty)<br><br>Be calibrated: most tasks are 1-2. Reserve 4-5 for genuine emotional difficulty.<br>"""<br><br>async def detect_avoidance(<br>    self,<br>    title: str,<br>    raw_input: str<br>) -> int:<br>    result = await self.ai.extract(<br>        text=f"Task: {title}\\nOriginal: {raw_input}",<br>        schema=AvoidanceAnalysis,<br>        system=AVOIDANCE_PROMPT<br>    )<br>    return result.weight<br>```<br><br>**Calibration Examples:**<br>```python<br>CALIBRATION = [<br>    ("Buy groceries", 1),<br>    ("Call the dentist", 2),<br>    ("Ugh, taxes", 4),<br>    ("I've been avoiding this for weeks", 4),<br>    ("The terrifying presentation", 5),<br>]<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Buy milk" scores 1. "Ugh, taxes" scores 4+. "That scary meeting" scores 4+. |
| **2** | **Test Logic** | **Given** "I dread calling them",<br>**When** detect_avoidance(),<br>**Then** weight >= 4.<br>**Given** "Pick up package",<br>**Then** weight <= 2. |
| **3** | **Formal Tests** | Run calibration examples. Assert each within ±1 of expected. Track accuracy over time. |

### D. Atomicity Validation

- **Yes.** Scoring logic only.

### E. Dependencies

- AGT-007 (AI provider).
- AGT-015 (Prompt versioning).

---

## AGT-010: Extract: Complexity

### A. User Story

> As a **System**, I want to **classify task complexity** so that I know when to prompt for breakdown before execution.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Classify each action as atomic (single step, <30 min), composite (multi-step, 30-120 min), or project (needs breakdown, >2 hours or requires planning). Composite and project tasks trigger breakdown prompts. |
| **2** | **Logic Flow** | 1. Analyze action title and context.<br>2. Consider estimated time as signal.<br>3. Look for multi-step indicators ("and then", "first...then").<br>4. Classify into enum.<br>5. Return classification with confidence. |
| **3** | **Formal Interfaces** | **Complexity Classifier:**<br>```python<br>from enum import Enum<br><br>class Complexity(str, Enum):<br>    ATOMIC = "atomic"      # Single focused action<br>    COMPOSITE = "composite"  # Multi-step but manageable<br>    PROJECT = "project"    # Needs planning/breakdown<br><br>class ComplexityAnalysis(BaseModel):<br>    complexity: Complexity<br>    suggested_steps: int  # Estimated number of sub-steps<br>    needs_breakdown: bool<br><br>COMPLEXITY_PROMPT = """<br>Classify this task's complexity for someone with executive function challenges.<br><br>ATOMIC: Can be done in one focused session without decisions<br>- "Send email to John"<br>- "Buy milk"<br>- "Call mom"<br><br>COMPOSITE: Has clear sub-steps but is still one task<br>- "Clean kitchen" (dishes, counters, floor)<br>- "Prepare presentation" (outline, slides, practice)<br><br>PROJECT: Requires planning, research, or multiple sessions<br>- "Do taxes"<br>- "Plan vacation"<br>- "Learn Python"<br><br>Err on the side of COMPOSITE for borderline cases - better to offer breakdown.<br>"""<br><br>async def classify_complexity(<br>    self,<br>    title: str,<br>    estimated_minutes: int<br>) -> ComplexityAnalysis:<br>    # Time is a strong signal<br>    if estimated_minutes <= 20:<br>        return ComplexityAnalysis(<br>            complexity=Complexity.ATOMIC,<br>            suggested_steps=1,<br>            needs_breakdown=False<br>        )<br>    <br>    result = await self.ai.extract(<br>        text=f"Task: {title} (estimated {estimated_minutes} minutes)",<br>        schema=ComplexityAnalysis,<br>        system=COMPLEXITY_PROMPT<br>    )<br>    return result<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Send email" = atomic. "Clean kitchen" = composite. "Do taxes" = project. |
| **2** | **Test Logic** | **Given** "Buy milk" (15 min),<br>**Then** complexity = ATOMIC.<br>**Given** "Prepare quarterly report" (120 min),<br>**Then** complexity = COMPOSITE or PROJECT. |
| **3** | **Formal Tests** | Test battery of known tasks. Assert correct classification. Monitor drift over time. |

### D. Atomicity Validation

- **Yes.** Classification logic only.

### E. Dependencies

- AGT-007 (AI provider).

---

## AGT-011: Extract: Confidence

### A. User Story

> As a **System**, I want to **assess extraction confidence** so that I can prompt the user to clarify ambiguous input.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Score how confident we are in the extraction from 0-1. Low confidence (<0.7) triggers validation UI. Factors: clear action words, specific context, unambiguous language. |
| **2** | **Logic Flow** | 1. During extraction, request confidence score.<br>2. Analyze: action verb present? Object clear? Time reasonable?<br>3. Return confidence with extraction.<br>4. UI checks confidence to show validation prompt.<br>5. After user confirms, update to confidence=1.0. |
| **3** | **Formal Interfaces** | **Confidence Scoring (in ExtractionResult):**<br>```python<br>class ExtractionResult(BaseModel):<br>    actions: list[ExtractedAction]<br>    confidence: float = Field(..., ge=0, le=1)<br>    ambiguities: list[str] = Field(default_factory=list)<br><br>CONFIDENCE_FACTORS = """<br>Score extraction confidence 0.0-1.0:<br><br>HIGH (0.9-1.0):<br>- Clear action verb (call, buy, send, write)<br>- Specific object (mom, groceries, report)<br>- Reasonable time estimate possible<br><br>MEDIUM (0.7-0.9):<br>- Action implied but not explicit<br>- Some ambiguity in scope<br>- Multiple valid interpretations<br><br>LOW (0.0-0.7):<br>- Vague language ("that thing", "stuff")<br>- No clear action<br>- Could mean many different tasks<br>- Emotional venting without task<br><br>List any ambiguities that the user might want to clarify.<br>"""<br>```<br><br>**Usage in UI:**<br>```typescript<br>if (result.confidence < 0.7) {<br>  showValidationPrompt(result.actions, result.ambiguities)<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Buy milk" = high confidence (~0.95). "That thing" = low confidence (~0.4). |
| **2** | **Test Logic** | **Given** "Call mom at 3pm",<br>**Then** confidence >= 0.9.<br>**Given** "The stuff",<br>**Then** confidence < 0.7. |
| **3** | **Formal Tests** | Test clear inputs have high confidence. Test vague inputs have low confidence. |

### D. Atomicity Validation

- **Yes.** Confidence scoring only.

### E. Dependencies

- AGT-008 (Part of extraction pipeline).

---

## AGT-012: Extract: Breakdown

### A. User Story

> As a **User**, I want to **break down overwhelming tasks** into tiny, physical first steps so I can actually start.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Given a complex task, generate 3-5 micro-steps that are physical, immediate, and take <10 minutes each. Focus on "initiation" - the first physical action to overcome paralysis. |
| **2** | **Logic Flow** | 1. Receive task title and context.<br>2. Call Claude with breakdown prompt.<br>3. Request 3-5 concrete steps.<br>4. Validate steps are physical (verb + object).<br>5. Return ordered step list. |
| **3** | **Formal Interfaces** | **Breakdown Service (app/services/breakdown.py):**<br>```python<br>class BreakdownStep(BaseModel):<br>    title: str = Field(..., max_length=50)<br>    is_physical: bool = True<br>    estimated_minutes: int = Field(default=5, le=15)<br><br>class BreakdownResult(BaseModel):<br>    steps: list[BreakdownStep] = Field(..., min_length=3, max_length=5)<br>    first_step_emphasis: str  # Why step 1 is the key<br><br>BREAKDOWN_PROMPT = """<br>You are an executive function coach helping someone who is paralyzed by a task.<br><br>Break this task into 3-5 MICRO-STEPS that are:<br>1. PHYSICAL - involve body movement, not just thinking<br>2. IMMEDIATE - can start right now with no preparation<br>3. TINY - each takes 2-10 minutes maximum<br>4. SEQUENTIAL - ordered by what comes first<br><br>Focus on INITIATION - the hardest part is starting.<br><br>BAD steps: "Research options", "Think about approach", "Plan the project"<br>GOOD steps: "Open laptop", "Create new document", "Write one sentence"<br><br>Example - "Clean kitchen":<br>1. Walk to kitchen sink (1 min)<br>2. Put dishes in dishwasher (5 min)<br>3. Wipe one counter (3 min)<br>4. Sweep floor in front of stove (5 min)<br>5. Take out trash bag (2 min)<br><br>Example - "Do taxes":<br>1. Open filing cabinet drawer (1 min)<br>2. Pull out W-2 forms (2 min)<br>3. Open TurboTax website (1 min)<br>4. Enter name and SSN (3 min)<br>5. Upload first document (2 min)<br>"""<br><br>class BreakdownService:<br>    async def breakdown(self, task_title: str) -> BreakdownResult:<br>        return await self.ai.extract(<br>            text=f"Break down: {task_title}",<br>            schema=BreakdownResult,<br>            system=BREAKDOWN_PROMPT<br>        )<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Do taxes" breaks into steps like "Open filing cabinet", not "Research tax software". Steps are concrete physical actions. |
| **2** | **Test Logic** | **Given** "Clean garage",<br>**When** breakdown(),<br>**Then** returns 3-5 steps.<br>**Then** each step starts with action verb.<br>**Then** no step mentions "think" or "plan". |
| **3** | **Formal Tests** | Test common complex tasks. Verify step count. Verify each contains physical verb. Verify estimated times < 15 min. |

### D. Atomicity Validation

- **Yes.** Breakdown generation only.

### E. Dependencies

- AGT-007 (AI provider).
- AGT-015 (Prompt versioning).

---

## AGT-013: Intent Classifier

### A. User Story

> As a **System**, I want to **understand what the user wants** so that I can route them to capture, coaching, or commands.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Classify user messages into intents: CAPTURE (adding tasks), COACHING (emotional support/stuck), COMMAND (system commands like /help). Use fast, low-token classification. |
| **2** | **Logic Flow** | 1. Check for command prefix (/).<br>2. If not command, analyze message content.<br>3. Look for task-like language → CAPTURE.<br>4. Look for emotional/stuck language → COACHING.<br>5. Default to CAPTURE if ambiguous.<br>6. Return intent with confidence. |
| **3** | **Formal Interfaces** | **Intent Classifier (app/services/intent.py):**<br>```python<br>from enum import Enum<br><br>class Intent(str, Enum):<br>    CAPTURE = "capture"    # Adding/managing tasks<br>    COACHING = "coaching"  # Emotional support, stuck<br>    COMMAND = "command"    # System commands<br><br>class IntentResult(BaseModel):<br>    intent: Intent<br>    confidence: float<br><br>INTENT_PROMPT = """<br>Classify user intent into exactly one category:<br><br>CAPTURE: User is dumping tasks, listing to-dos, or planning<br>- "Buy milk and eggs"<br>- "I need to call mom"<br>- "Add: finish report"<br><br>COACHING: User is expressing emotions, feeling stuck, or asking for help<br>- "I can't focus today"<br>- "I'm overwhelmed"<br>- "Why is this so hard?"<br>- "I feel stuck"<br><br>Respond with just the intent name.<br>"""<br><br>class IntentClassifier:<br>    async def classify(self, text: str) -> IntentResult:<br>        # Fast path: commands<br>        if text.startswith('/'):<br>            return IntentResult(intent=Intent.COMMAND, confidence=1.0)<br>        <br>        # Fast path: obvious capture (starts with action verb)<br>        action_starters = ['buy', 'call', 'send', 'email', 'write', 'do', 'finish', 'complete']<br>        if any(text.lower().startswith(v) for v in action_starters):<br>            return IntentResult(intent=Intent.CAPTURE, confidence=0.95)<br>        <br>        # AI classification for ambiguous cases<br>        response = await self.ai.complete(<br>            messages=[{"role": "user", "content": text}],<br>            system=INTENT_PROMPT,<br>            max_tokens=10<br>        )<br>        intent_str = response.content.strip().upper()<br>        return IntentResult(<br>            intent=Intent[intent_str],<br>            confidence=0.85<br>        )<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | "Buy groceries" = CAPTURE. "I feel stuck" = COACHING. "/help" = COMMAND. |
| **2** | **Test Logic** | **Given** "I need to call mom",<br>**Then** intent = CAPTURE.<br>**Given** "I can't do this",<br>**Then** intent = COACHING. |
| **3** | **Formal Tests** | Test suite of 20+ examples per intent. Assert >90% accuracy. |

### D. Atomicity Validation

- **Yes.** Classification only.

### E. Dependencies

- AGT-007 (AI provider for ambiguous cases).

---

## AGT-014: Coaching Handler

### A. User Story

> As a **User**, I want to **talk to a supportive assistant** when I'm stuck so I can process emotions and find a way forward.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Provide a conversational coaching experience for stuck users. Validate feelings first, then gently guide toward one small action. Maintain context of current task if applicable. Support multi-turn conversation. |
| **2** | **Logic Flow** | 1. Receive user message and conversation history.<br>2. If first message, acknowledge emotion.<br>3. Maintain coaching context (current task, previous exchanges).<br>4. Generate empathetic, action-oriented response.<br>5. Stream response to UI.<br>6. If user identifies action, offer to add it. |
| **3** | **Formal Interfaces** | **Coaching Service (app/services/coaching.py):**<br>```python<br>COACHING_SYSTEM = """<br>You are a compassionate executive function coach. The user is struggling.<br><br>Your approach:<br>1. VALIDATE first - acknowledge feelings without minimizing<br>2. NORMALIZE - "This is hard for everyone" / "ADHD makes this harder"<br>3. TINY STEP - suggest the smallest possible action (2 minutes max)<br>4. NO SHAME - never imply they should have done better<br><br>Response style:<br>- Warm but not saccharine<br>- Brief (2-4 sentences usually)<br>- End with one small suggestion or question<br>- Use "we" language when appropriate<br><br>Examples:<br>User: "I can't focus on anything today"<br>You: "That's frustrating, especially when you have things you want to do. Some days our brains just won't cooperate. What if we just pick ONE thing - even just opening a document counts as a win?"<br><br>User: "I've been avoiding this for weeks"<br>You: "That sounds heavy to carry around. The avoiding makes sense - our brains protect us from things that feel overwhelming. What's the tiniest piece of this we could look at for just 2 minutes?"<br><br>NEVER say:<br>- "Just do it"<br>- "It's not that hard"<br>- "You should have..."<br>- "Why don't you just..."<br>"""<br><br>class CoachingService:<br>    async def process(<br>        self,<br>        message: str,<br>        user: User,<br>        conversation_history: list[Message],<br>        current_task: Action | None = None<br>    ) -> AsyncIterator[str]:<br>        context = ""<br>        if current_task:<br>            context = f"\\n\\nContext: User is working on '{current_task.title}'"<br>        <br>        messages = conversation_history + [<br>            {"role": "user", "content": message}<br>        ]<br>        <br>        async for chunk in self.ai.stream(<br>            messages=messages,<br>            system=COACHING_SYSTEM + context<br>        ):<br>            yield chunk<br>```<br><br>**Conversation Management:**<br>```python<br>class CoachingConversation:<br>    def __init__(self, user_id: str, task_id: str | None = None):<br>        self.messages: list[Message] = []<br>        self.user_id = user_id<br>        self.task_id = task_id<br>    <br>    def add_message(self, role: str, content: str):<br>        self.messages.append(Message(role=role, content=content))<br>    <br>    def get_history(self, limit: int = 10) -> list[Message]:<br>        return self.messages[-limit:]<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Say "I can't do this." Response validates feeling, doesn't shame, suggests tiny action. Response streams in real-time. |
| **2** | **Test Logic** | **Given** "I'm stuck and frustrated",<br>**When** coaching processes,<br>**Then** response contains validation language.<br>**Then** response suggests small action.<br>**Then** response doesn't contain shame words. |
| **3** | **Formal Tests** | Test with emotional inputs. Check for validation keywords. Check absence of shame patterns. Check streaming works. |

### D. Atomicity Validation

- **Yes.** Coaching logic only.

### E. Dependencies

- AGT-007 (AI provider with streaming).
- AGT-006 (SSE streaming for responses).

---

## AGT-015: Prompt Versioning

### A. User Story

> As a **Developer**, I want to **version and track prompts** so that I can iterate on them and understand what's deployed.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Store all prompts as versioned templates. Log which version was used for each AI call. Support A/B testing of prompt variations. Enable rollback to previous versions. |
| **2** | **Logic Flow** | 1. Define prompts in versioned files or database.<br>2. Each prompt has: name, version, content, created_at.<br>3. When using prompt, record version in intent_log.<br>4. Admin can view usage stats per version.<br>5. New versions can be deployed without code changes. |
| **3** | **Formal Interfaces** | **Prompt Registry (app/prompts/registry.py):**<br>```python<br>from dataclasses import dataclass<br>from datetime import datetime<br><br>@dataclass<br>class PromptVersion:<br>    name: str<br>    version: str<br>    content: str<br>    created_at: datetime<br>    is_active: bool = True<br><br>class PromptRegistry:<br>    def __init__(self):<br>        self._prompts: dict[str, PromptVersion] = {}<br>        self._load_prompts()<br>    <br>    def get(self, name: str) -> PromptVersion:<br>        if name not in self._prompts:<br>            raise KeyError(f"Prompt '{name}' not found")<br>        return self._prompts[name]<br>    <br>    def _load_prompts(self):<br>        # Load from files or database<br>        self._prompts = {<br>            "extraction": PromptVersion(<br>                name="extraction",<br>                version="1.0.0",<br>                content=EXTRACTION_PROMPT,<br>                created_at=datetime.now()<br>            ),<br>            "coaching": PromptVersion(...),<br>            "breakdown": PromptVersion(...),<br>        }<br><br>prompt_registry = PromptRegistry()<br>```<br><br>**Prompt Files Structure:**<br>```<br>app/prompts/<br>  extraction/<br>    v1.0.0.txt<br>    v1.1.0.txt  # current<br>  coaching/<br>    v1.0.0.txt<br>  breakdown/<br>    v1.0.0.txt<br>```<br><br>**Logging Version:**<br>```python<br>async def log_intent(user_id, raw_input, intent, extraction, response):<br>    await supabase.table('intent_log').insert({<br>        ...,<br>        'prompt_version': prompt_registry.get('extraction').version<br>    }).execute()<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Get prompt by name. Returns version info. Update prompt file. Next request uses new content. |
| **2** | **Test Logic** | **Given** prompt "extraction" exists,<br>**When** registry.get("extraction"),<br>**Then** returns PromptVersion with content. |
| **3** | **Formal Tests** | Register test prompt. Get it. Assert fields. Check intent_log includes version. |

### D. Atomicity Validation

- **Yes.** Versioning infrastructure only.

### E. Dependencies

- SUB-001 (Database Schema - for prompt storage table).

**Note:** INF-007 (Intent Log Recording) depends on this feature to log version IDs.

---

## AGT-016: Extraction Orchestrator

### A. User Story

> As the **System**, I want to **coordinate all extraction operations** so that user input produces complete, validated action data.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Orchestrates extraction pipeline: action extraction → avoidance weight → complexity → confidence. Returns unified result with all extracted fields. Handles partial failures gracefully. |
| **2** | **Logic Flow** | 1. Receive raw text input.<br>2. Call AGT-008 (action extraction).<br>3. If action extracted, parallel call AGT-009 (avoidance) + AGT-010 (complexity).<br>4. Call AGT-011 (confidence) on combined result.<br>5. Return unified ExtractionResult. |
| **3** | **Formal Interfaces** | **Extraction Orchestrator (app/services/extraction_orchestrator.py):**<br>```python<br>from dataclasses import dataclass<br>from typing import Optional<br>import asyncio<br><br>@dataclass<br>class ExtractionResult:<br>    action: Optional[ExtractedAction]<br>    avoidance_weight: int<br>    complexity: ComplexityLevel<br>    confidence: float<br>    raw_response: dict<br><br>class ExtractionOrchestrator:<br>    def __init__(<br>        self,<br>        action_extractor: ActionExtractor,      # AGT-008<br>        avoidance_extractor: AvoidanceExtractor, # AGT-009<br>        complexity_extractor: ComplexityExtractor, # AGT-010<br>        confidence_scorer: ConfidenceScorer      # AGT-011<br>    ):<br>        self.action = action_extractor<br>        self.avoidance = avoidance_extractor<br>        self.complexity = complexity_extractor<br>        self.confidence = confidence_scorer<br><br>    async def extract(self, text: str, context: Optional[dict] = None) -> ExtractionResult:<br>        # Step 1: Extract action<br>        action_result = await self.action.extract(text, context)<br>        <br>        if not action_result.action:<br>            return ExtractionResult(<br>                action=None,<br>                avoidance_weight=0,<br>                complexity=ComplexityLevel.SIMPLE,<br>                confidence=0.0,<br>                raw_response=action_result.raw<br>            )<br>        <br>        # Step 2: Parallel extraction of metadata<br>        avoidance_task = self.avoidance.extract(action_result.action)<br>        complexity_task = self.complexity.extract(action_result.action)<br>        <br>        avoidance_result, complexity_result = await asyncio.gather(<br>            avoidance_task, complexity_task<br>        )<br>        <br>        # Step 3: Calculate confidence<br>        confidence = await self.confidence.score(<br>            action=action_result.action,<br>            avoidance=avoidance_result,<br>            complexity=complexity_result<br>        )<br>        <br>        return ExtractionResult(<br>            action=action_result.action,<br>            avoidance_weight=avoidance_result.weight,<br>            complexity=complexity_result.level,<br>            confidence=confidence.score,<br>            raw_response={<br>                'action': action_result.raw,<br>                'avoidance': avoidance_result.raw,<br>                'complexity': complexity_result.raw,<br>                'confidence': confidence.raw<br>            }<br>        )<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send text "Call mom tomorrow". Get back action with title, avoidance weight, complexity, and confidence score. All fields populated. |
| **2** | **Test Logic** | **Given** extractable text,<br>**Then** action extracted.<br>**Then** avoidance weight 1-5.<br>**Then** complexity simple/medium/complex.<br>**Then** confidence 0.0-1.0. |
| **3** | **Formal Tests** | Mock all extractors. Test full pipeline. Test partial failure (action extracts but avoidance fails). Verify graceful degradation. |

### D. Atomicity Validation

- **Yes.** Orchestration only. Individual extractors handle their own prompts/parsing.

### E. Dependencies

- AGT-008 (Extract: Actions).
- AGT-009 (Extract: Avoidance Weight).
- AGT-010 (Extract: Complexity).
- AGT-011 (Extract: Confidence).

### F. Complexity

**Medium** - Pipeline coordination, parallel execution, error handling.

---

*End of Agentic Specifications*
