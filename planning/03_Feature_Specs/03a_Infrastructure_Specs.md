# Infrastructure Feature Specifications

**Category:** INF (Infrastructure)
**Total Features:** 11
**Complexity:** 9 Easy, 2 Medium

---

## INF-001: Next.js Setup

### A. User Story

> As a **Developer**, I want to **initialize a Next.js 14+ project with App Router and Tailwind CSS** so that I have a modern, type-safe foundation for the frontend.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a new Next.js project using create-next-app with TypeScript enabled. Configure Tailwind CSS with the project's color palette. Set up the App Router structure with initial layout and page files. Configure path aliases for clean imports. |
| **2** | **Logic Flow** | 1. Run `npx create-next-app@latest` with TypeScript, Tailwind, ESLint, App Router options.<br>2. Configure `tailwind.config.ts` with custom colors (gray-100 background, semantic colors).<br>3. Create base layout at `app/layout.tsx` with metadata.<br>4. Create placeholder `app/page.tsx`.<br>5. Configure `tsconfig.json` path aliases (`@/*` → `src/*`). |
| **3** | **Formal Interfaces** | **Directory Structure:**<br>`app/layout.tsx` - Root layout with html/body<br>`app/page.tsx` - Landing/redirect page<br>`tailwind.config.ts` - Theme configuration<br>`next.config.js` - Next.js configuration<br><br>**Scripts (package.json):**<br>`dev`: `next dev`<br>`build`: `next build`<br>`start`: `next start` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Run the dev server. Browser shows the placeholder page without errors. Tailwind classes apply correctly. TypeScript compilation succeeds. |
| **2** | **Test Logic** | **Given** the project is initialized,<br>**When** I run `npm run dev`,<br>**Then** server starts on localhost:3000.<br>**When** I run `npm run build`,<br>**Then** build completes without errors. |
| **3** | **Formal Tests** | `npm run build` exits with code 0. `curl localhost:3000` returns 200 OK with HTML content. |

### D. Atomicity Validation

- **Yes.** Single project initialization task with no business logic.

### E. Dependencies

- None (foundation feature).

---

## INF-002: FastAPI Setup

### A. User Story

> As a **Developer**, I want to **initialize a FastAPI project with proper structure** so that I have a scalable foundation for the AI backend.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a Python project with FastAPI as the web framework. Use Poetry or pip for dependency management. Set up a modular folder structure with routers, services, and models directories. Configure Pydantic settings for environment variables. |
| **2** | **Logic Flow** | 1. Initialize project with `pyproject.toml` or `requirements.txt`.<br>2. Install dependencies: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`.<br>3. Create `app/main.py` with FastAPI app instance.<br>4. Create folder structure: `app/routers/`, `app/services/`, `app/models/`.<br>5. Create `app/config.py` with Settings class. |
| **3** | **Formal Interfaces** | **Directory Structure:**<br>`app/main.py` - FastAPI app entry point<br>`app/config.py` - Pydantic Settings<br>`app/routers/` - API route modules<br>`app/services/` - Business logic<br>`app/models/` - Pydantic models<br><br>**Config Class:**<br>```python<br>class Settings(BaseSettings):<br>    supabase_url: str<br>    supabase_service_key: str<br>    anthropic_api_key: str<br>    class Config:<br>        env_file = ".env"<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Run the server locally with uvicorn. The root endpoint returns a welcome message. OpenAPI docs are accessible at /docs. |
| **2** | **Test Logic** | **Given** the server is running,<br>**When** GET /,<br>**Then** return 200 with JSON message.<br>**When** GET /docs,<br>**Then** return Swagger UI HTML. |
| **3** | **Formal Tests** | `uvicorn app.main:app --host 0.0.0.0 --port 8000` starts without errors. `curl localhost:8000/` returns `{"message": "Executive Function Prosthetic API"}`. |

### D. Atomicity Validation

- **Yes.** Single project setup task.

### E. Dependencies

- None (foundation feature).

---

## INF-003: Vercel Config

### A. User Story

> As a **Developer**, I want to **configure Vercel deployment** so that the frontend automatically deploys from the main branch.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a vercel.json configuration file specifying build settings, environment variables mapping, and routing rules. Configure the project to use the Next.js framework preset. |
| **2** | **Logic Flow** | 1. Create `vercel.json` in frontend root.<br>2. Specify `framework: "nextjs"`.<br>3. Configure environment variable references.<br>4. Set up rewrites for API proxy if needed.<br>5. Configure headers for security (CSP, etc.). |
| **3** | **Formal Interfaces** | **vercel.json:**<br>```json<br>{<br>  "framework": "nextjs",<br>  "buildCommand": "npm run build",<br>  "env": {<br>    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",<br>    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key",<br>    "NEXT_PUBLIC_API_URL": "@api-url"<br>  }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Push to main branch. Vercel automatically builds and deploys. Preview deployments work on PRs. |
| **2** | **Test Logic** | **Given** valid vercel.json,<br>**When** Vercel CLI runs `vercel build`,<br>**Then** build succeeds locally. |
| **3** | **Formal Tests** | `vercel build` (or `next build`) exits with code 0. Deployed URL responds with 200. |

### D. Atomicity Validation

- **Yes.** Configuration file only.

### E. Dependencies

- INF-001 (Next.js project must exist).

---

## INF-004: Railway Config

### A. User Story

> As a **Developer**, I want to **configure Railway deployment for the backend** so that the FastAPI service auto-deploys with cron job support.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a railway.toml or Dockerfile for the FastAPI backend. Configure environment variables, health check endpoint, and cron job scheduling for background tasks. |
| **2** | **Logic Flow** | 1. Create `Dockerfile` for Python 3.11+ with FastAPI.<br>2. Create `railway.toml` with build and deploy config.<br>3. Configure start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.<br>4. Set up cron service for scheduled jobs (hourly triggers).<br>5. Configure health check path. |
| **3** | **Formal Interfaces** | **Dockerfile:**<br>```dockerfile<br>FROM python:3.11-slim<br>WORKDIR /app<br>COPY requirements.txt .<br>RUN pip install -r requirements.txt<br>COPY . .<br>CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]<br>```<br><br>**railway.toml:**<br>```toml<br>[build]<br>builder = "dockerfile"<br><br>[deploy]<br>healthcheckPath = "/health"<br>restartPolicyType = "on_failure"<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Push to main. Railway builds and deploys the container. Health check passes. Cron jobs trigger on schedule. |
| **2** | **Test Logic** | **Given** valid Dockerfile,<br>**When** `docker build .`,<br>**Then** image builds successfully.<br>**When** container runs,<br>**Then** /health returns 200. |
| **3** | **Formal Tests** | `docker build -t backend .` exits with code 0. `docker run -p 8000:8000 backend` starts and responds to requests. |

### D. Atomicity Validation

- **Yes.** Deployment configuration only.

### E. Dependencies

- INF-002 (FastAPI project must exist).

---

## INF-005: Environment Config

### A. User Story

> As a **Developer**, I want to **manage environment variables consistently** across development, staging, and production environments.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create .env.example files documenting all required environment variables. Set up validation to fail fast if required variables are missing. Configure different .env files for local development. |
| **2** | **Logic Flow** | 1. Create `.env.example` in both frontend and backend roots.<br>2. Document all variables with descriptions.<br>3. Backend: Use Pydantic Settings to validate on startup.<br>4. Frontend: Use Next.js env validation in `next.config.js`.<br>5. Add `.env*` to `.gitignore`. |
| **3** | **Formal Interfaces** | **Backend .env.example:**<br>```<br># Supabase<br>SUPABASE_URL=https://xxx.supabase.co<br>SUPABASE_SERVICE_KEY=eyJ...<br><br># AI Services<br>ANTHROPIC_API_KEY=sk-ant-...<br>DEEPGRAM_API_KEY=...<br><br># Telegram<br>TELEGRAM_BOT_TOKEN=...<br>TELEGRAM_SECRET_TOKEN=...<br><br># Email<br>RESEND_API_KEY=re_...<br>```<br><br>**Frontend .env.example:**<br>```<br>NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co<br>NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...<br>NEXT_PUBLIC_API_URL=https://api.example.com<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Start the backend without required env vars. It should fail with a clear error message listing missing variables. |
| **2** | **Test Logic** | **Given** SUPABASE_URL is unset,<br>**When** starting the backend,<br>**Then** raise ValidationError with field name. |
| **3** | **Formal Tests** | Unset required env var, run `python -c "from app.config import settings"`, assert raises `ValidationError`. |

### D. Atomicity Validation

- **Yes.** Configuration files and validation only.

### E. Dependencies

- INF-001 (Frontend project).
- INF-002 (Backend project).

---

## INF-006: Structured Logging

### A. User Story

> As a **Developer**, I want to **implement structured JSON logging** so that logs are searchable and parseable in production monitoring tools.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Configure Python's logging to output JSON in production. Include request IDs, user IDs, and timestamps in every log entry. Use human-readable format in development. |
| **2** | **Logic Flow** | 1. Install `python-json-logger` or use `structlog`.<br>2. Create logging configuration in `app/logging_config.py`.<br>3. Configure based on environment (JSON for prod, colored for dev).<br>4. Add middleware to inject request_id into log context.<br>5. Create helper functions for consistent log calls. |
| **3** | **Formal Interfaces** | **Log Format (Production):**<br>```json<br>{<br>  "timestamp": "2025-12-09T10:00:00Z",<br>  "level": "INFO",<br>  "message": "Action extracted",<br>  "request_id": "uuid",<br>  "user_id": "uuid",<br>  "action_count": 3<br>}<br>```<br><br>**Logger Usage:**<br>```python<br>from app.logging_config import get_logger<br>logger = get_logger(__name__)<br>logger.info("Action extracted", action_count=3)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Make an API request. Check logs contain JSON with timestamp, level, message, and request_id. |
| **2** | **Test Logic** | **Given** ENV=production,<br>**When** logger.info("test") is called,<br>**Then** output is valid JSON with required fields. |
| **3** | **Formal Tests** | Capture stdout, parse as JSON, assert keys `timestamp`, `level`, `message` exist. |

### D. Atomicity Validation

- **Yes.** Logging infrastructure only.

### E. Dependencies

- INF-002 (FastAPI project).

---

## INF-007: Intent Log Recording

### A. User Story

> As a **System**, I want to **record all user intents and AI responses** so that I can analyze patterns and improve extraction accuracy over time.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a database table to store every user message, the classified intent, the AI's response, and any extracted data. This serves as training data for prompt improvements. |
| **2** | **Logic Flow** | 1. Create `intent_log` table in Supabase.<br>2. Create service function `log_intent(user_id, raw_input, intent, extraction, response)`.<br>3. Call after every AI processing completes.<br>4. Apply RLS: users can't read their own logs (privacy/security). |
| **3** | **Formal Interfaces** | **Table Schema:**<br>```sql<br>CREATE TABLE intent_log (<br>  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),<br>  user_id UUID REFERENCES auth.users NOT NULL,<br>  raw_input TEXT NOT NULL,<br>  classified_intent TEXT,<br>  extraction_result JSONB,<br>  ai_response TEXT,<br>  prompt_version TEXT,<br>  created_at TIMESTAMPTZ DEFAULT NOW()<br>);<br>```<br><br>**Service Function:**<br>```python<br>async def log_intent(<br>    user_id: str,<br>    raw_input: str,<br>    intent: str,<br>    extraction: dict | None,<br>    response: str<br>) -> None<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Process a user message. Check the intent_log table contains a new row with all fields populated. |
| **2** | **Test Logic** | **Given** user sends "Buy milk",<br>**When** extraction completes,<br>**Then** intent_log has row with raw_input="Buy milk", intent="CAPTURE". |
| **3** | **Formal Tests** | Insert via service function, query table, assert row exists with correct user_id and input. |

### D. Atomicity Validation

- **Yes.** Logging infrastructure only.

### E. Dependencies

- SUB-001 (Database schema must exist).
- INF-002 (FastAPI project).

---

## INF-008: Error Middleware

### A. User Story

> As a **Developer**, I want to **centralize error handling** so that all exceptions return consistent JSON responses and are properly logged.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create FastAPI middleware that catches all unhandled exceptions, logs them with stack traces, and returns a sanitized JSON error response. Different handling for validation errors vs. server errors. |
| **2** | **Logic Flow** | 1. Create custom exception classes (NotFoundError, ValidationError, etc.).<br>2. Create exception handlers for each type.<br>3. Create catch-all handler for unexpected errors.<br>4. Log error with request context.<br>5. Return JSON with error code, message, and request_id. |
| **3** | **Formal Interfaces** | **Error Response Schema:**<br>```python<br>class ErrorResponse(BaseModel):<br>    error: str  # Error code<br>    message: str  # Human-readable<br>    request_id: str<br>    details: dict | None = None<br>```<br><br>**Exception Handlers:**<br>```python<br>@app.exception_handler(ValidationError)<br>async def validation_handler(request, exc):<br>    return JSONResponse(status_code=400, content={...})<br><br>@app.exception_handler(Exception)<br>async def generic_handler(request, exc):<br>    logger.exception("Unhandled error")<br>    return JSONResponse(status_code=500, content={...})<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Trigger an unhandled exception. Response is JSON with error details. Stack trace appears in logs but not in response. |
| **2** | **Test Logic** | **Given** endpoint raises RuntimeError,<br>**When** client calls endpoint,<br>**Then** response is 500 with JSON body containing `error` and `request_id`. |
| **3** | **Formal Tests** | Create test endpoint that raises. Call it. Assert response schema matches ErrorResponse. Assert logs contain exception. |

### D. Atomicity Validation

- **Yes.** Middleware and handlers only.

### E. Dependencies

- INF-002 (FastAPI project).
- INF-006 (Structured logging).

---

## INF-009: Health Endpoint

### A. User Story

> As a **DevOps Engineer**, I want to **check service health** so that monitoring tools can verify the API is running and connected to dependencies.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a /health endpoint that checks database connectivity and returns service status. Include version information and uptime. |
| **2** | **Logic Flow** | 1. Create GET /health endpoint.<br>2. Attempt lightweight DB query (SELECT 1).<br>3. Return status object with checks.<br>4. If any check fails, return 503 with failure details. |
| **3** | **Formal Interfaces** | **Endpoint:** `GET /health`<br><br>**Response (Healthy):**<br>```json<br>{<br>  "status": "healthy",<br>  "version": "1.0.0",<br>  "checks": {<br>    "database": "ok",<br>    "uptime_seconds": 3600<br>  }<br>}<br>```<br><br>**Response (Unhealthy - 503):**<br>```json<br>{<br>  "status": "unhealthy",<br>  "checks": {<br>    "database": "failed: connection timeout"<br>  }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Call /health. Get 200 with status "healthy" when DB is up. Disconnect DB, call again, get 503. |
| **2** | **Test Logic** | **Given** database is connected,<br>**When** GET /health,<br>**Then** status=200, body.status="healthy". |
| **3** | **Formal Tests** | `response = client.get("/health")` → assert `response.status_code == 200` and `response.json()["status"] == "healthy"`. |

### D. Atomicity Validation

- **Yes.** Single endpoint.

### E. Dependencies

- INF-002 (FastAPI project).
- INT-001 (Supabase client for DB check).

---

## INF-010: Onboarding Flow

### A. User Story

> As a **New User**, I want to **be guided through initial setup** so that the system knows my timezone and preferred notification channel.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a conversational onboarding that activates on first login. Ask for timezone (detect from browser, confirm). Explain how to connect Telegram. Mark onboarding complete in profile. |
| **2** | **Logic Flow** | 1. Check `profile.onboarding_completed` on login.<br>2. If false, show onboarding overlay/page.<br>3. Step 1: Confirm timezone (auto-detect, allow change).<br>4. Step 2: Show Telegram linking instructions + unique code.<br>5. Step 3: Quick tutorial of core workflow.<br>6. On finish: Update profile `onboarding_completed = true`. |
| **3** | **Formal Interfaces** | **Frontend Components:**<br>`<OnboardingWizard steps={[...]} onComplete={handleComplete} />`<br><br>**API Endpoint:**<br>`PATCH /api/profile` with body `{ timezone: "America/New_York", onboarding_completed: true }`<br><br>**Profile Check:**<br>```typescript<br>if (!profile.onboarding_completed) {<br>  router.push('/onboarding')<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | New user logs in, sees onboarding wizard. Completes all steps. Profile is updated. Next login goes directly to dashboard. |
| **2** | **Test Logic** | **Given** new user with onboarding_completed=false,<br>**When** accessing /dashboard,<br>**Then** redirect to /onboarding.<br>**When** onboarding completes,<br>**Then** profile.onboarding_completed=true. |
| **3** | **Formal Tests** | E2E test: Create new user, verify redirect, complete wizard, verify profile update, verify no redirect on next visit. |

### D. Atomicity Validation

- **Yes.** Onboarding UI and logic only.

### E. Dependencies

- SUB-003 (Authentication must work).
- SUB-005 (Profile management).
- FE-014 (Responsive layout for wizard display).

---

## INF-011: CORS Configuration

### A. User Story

> As a **Developer**, I want to **configure CORS** so that the frontend can securely communicate with the backend API.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Add CORS middleware to FastAPI allowing requests from the frontend origin. Configure allowed methods, headers, and credentials. Restrict origins in production. |
| **2** | **Logic Flow** | 1. Import CORSMiddleware from FastAPI.<br>2. Read allowed origins from environment variable.<br>3. Add middleware with allow_credentials=True.<br>4. Allow specific headers (Authorization, Content-Type).<br>5. Allow specific methods (GET, POST, PUT, PATCH, DELETE, OPTIONS). |
| **3** | **Formal Interfaces** | **Configuration:**<br>```python<br>from fastapi.middleware.cors import CORSMiddleware<br><br>origins = settings.allowed_origins.split(",")<br><br>app.add_middleware(<br>    CORSMiddleware,<br>    allow_origins=origins,<br>    allow_credentials=True,<br>    allow_methods=["*"],<br>    allow_headers=["*"],<br>)<br>```<br><br>**Environment Variable:**<br>`ALLOWED_ORIGINS=https://app.example.com,http://localhost:3000` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Frontend makes request to backend. No CORS errors in browser console. Response includes appropriate CORS headers. |
| **2** | **Test Logic** | **Given** frontend origin is in allowed list,<br>**When** making cross-origin request,<br>**Then** response includes `Access-Control-Allow-Origin` header. |
| **3** | **Formal Tests** | Send OPTIONS request with Origin header, assert response has CORS headers. |

### D. Atomicity Validation

- **Yes.** Middleware configuration only.

### E. Dependencies

- INF-002 (FastAPI project).

---

*End of Infrastructure Specifications*
