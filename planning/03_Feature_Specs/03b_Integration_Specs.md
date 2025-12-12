# Integration Feature Specifications

**Category:** INT (Integration)
**Total Features:** 6
**Complexity:** 4 Easy, 2 Medium

---

## INT-001: Supabase Client

### A. User Story

> As a **Developer**, I want to **initialize and configure the Supabase client** so that both frontend and backend can interact with the database securely.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create Supabase client instances for frontend (with anon key for RLS) and backend (with service key for admin operations). Handle connection pooling and error recovery. |
| **2** | **Logic Flow** | **Frontend:**<br>1. Import `createClientComponentClient` from `@supabase/auth-helpers-nextjs`.<br>2. Create singleton client with public URL and anon key.<br>3. Export typed client.<br><br>**Backend:**<br>1. Import `create_client` from `supabase`.<br>2. Create client with URL and service role key.<br>3. Export as singleton. |
| **3** | **Formal Interfaces** | **Frontend (lib/supabase.ts):**<br>```typescript<br>import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'<br>import { Database } from '@/types/supabase'<br><br>export const supabase = createClientComponentClient<Database>()<br>```<br><br>**Backend (app/clients/supabase.py):**<br>```python<br>from supabase import create_client, Client<br>from app.config import settings<br><br>supabase: Client = create_client(<br>    settings.supabase_url,<br>    settings.supabase_service_key<br>)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Frontend client can query public data. Backend client can bypass RLS for admin operations. Both handle network errors gracefully. |
| **2** | **Test Logic** | **Given** valid credentials,<br>**When** `supabase.from('profiles').select('*')`,<br>**Then** returns data or empty array, no error. |
| **3** | **Formal Tests** | Backend: `result = supabase.table('profiles').select('*').execute()` → assert `result.data is not None`. |

### D. Atomicity Validation

- **Yes.** Client initialization only.

### E. Dependencies

- INF-005 (Environment configuration).

---

## INT-002: Claude API Client

### A. User Story

> As a **Developer**, I want to **wrap the Anthropic Claude API** so that AI features have a consistent interface with error handling and rate limiting.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a client wrapper for Claude API that handles authentication, message formatting, streaming responses, and structured output parsing. Include retry logic for transient failures. |
| **2** | **Logic Flow** | 1. Import Anthropic SDK.<br>2. Create client with API key.<br>3. Create `chat_completion` function with messages parameter.<br>4. Create `structured_extraction` function for JSON output.<br>5. Handle rate limits with exponential backoff.<br>6. Return typed responses. |
| **3** | **Formal Interfaces** | **Client (app/clients/claude.py):**<br>```python<br>from anthropic import Anthropic<br>from pydantic import BaseModel<br>from typing import AsyncIterator<br><br>class ClaudeClient:<br>    def __init__(self, api_key: str):<br>        self.client = Anthropic(api_key=api_key)<br>        self.model = "claude-sonnet-4-20250514"<br>    <br>    async def chat(<br>        self,<br>        messages: list[dict],<br>        system: str | None = None,<br>        max_tokens: int = 1024<br>    ) -> str: ...<br>    <br>    async def chat_stream(<br>        self,<br>        messages: list[dict],<br>        system: str | None = None<br>    ) -> AsyncIterator[str]: ...<br>    <br>    async def extract[T: BaseModel](<br>        self,<br>        text: str,<br>        schema: type[T],<br>        system: str<br>    ) -> T: ...<br>```<br><br>**Usage:**<br>```python<br>claude = ClaudeClient(settings.anthropic_api_key)<br>result = await claude.extract(user_input, ActionList, EXTRACTION_PROMPT)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send a simple message, receive text response. Send extraction request, receive parsed Pydantic model. Handle API errors gracefully. |
| **2** | **Test Logic** | **Given** valid API key,<br>**When** `claude.chat([{"role": "user", "content": "Hello"}])`,<br>**Then** returns non-empty string.<br>**Given** invalid API key,<br>**Then** raises AuthenticationError. |
| **3** | **Formal Tests** | Mock Anthropic client. Test chat returns string. Test extract returns parsed model. Test retry on 429. |

### D. Atomicity Validation

- **Yes.** Client wrapper only.

### E. Dependencies

- INF-005 (Environment configuration for API key).

---

## INT-003: Deepgram Client

### A. User Story

> As a **Developer**, I want to **wrap the Deepgram API** so that voice transcription is handled consistently with error recovery.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a client wrapper for Deepgram that handles audio transcription using the Nova-2 model. Accept audio bytes or URLs, return transcribed text with punctuation. |
| **2** | **Logic Flow** | 1. Import Deepgram SDK.<br>2. Create client with API key.<br>3. Create `transcribe` function accepting audio bytes.<br>4. Configure: model="nova-2", smart_format=true, punctuate=true.<br>5. Extract transcript from response.<br>6. Handle API errors. |
| **3** | **Formal Interfaces** | **Client (app/clients/deepgram.py):**<br>```python<br>from deepgram import DeepgramClient, PrerecordedOptions<br><br>class DeepgramTranscriber:<br>    def __init__(self, api_key: str):<br>        self.client = DeepgramClient(api_key)<br>        self.options = PrerecordedOptions(<br>            model="nova-2",<br>            smart_format=True,<br>            punctuate=True,<br>            language="en"<br>        )<br>    <br>    async def transcribe(self, audio_bytes: bytes) -> str:<br>        """Transcribe audio bytes to text."""<br>        response = await self.client.listen.prerecorded.v("1").transcribe_file(<br>            {"buffer": audio_bytes, "mimetype": "audio/webm"},<br>            self.options<br>        )<br>        return response.results.channels[0].alternatives[0].transcript<br>    <br>    async def transcribe_url(self, audio_url: str) -> str:<br>        """Transcribe audio from URL."""<br>        ...<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Upload audio file, receive transcribed text. Audio with speech returns non-empty string. Silent audio returns empty or minimal text. |
| **2** | **Test Logic** | **Given** audio with clear speech,<br>**When** `transcribe(audio_bytes)`,<br>**Then** returns string containing expected words. |
| **3** | **Formal Tests** | Mock Deepgram response. Test transcript extraction. Test error handling for invalid audio. |

### D. Atomicity Validation

- **Yes.** Client wrapper only.

### E. Dependencies

- INF-005 (Environment configuration for API key).

---

## INT-004: Telegram API Client

### A. User Story

> As a **Developer**, I want to **wrap the Telegram Bot API** so that sending and receiving messages is straightforward and type-safe.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a client for Telegram Bot API with methods for sending messages, setting webhooks, and downloading files (for voice notes). Use httpx for async HTTP. |
| **2** | **Logic Flow** | 1. Create TelegramClient class with bot token.<br>2. Implement `send_message(chat_id, text)` using sendMessage API.<br>3. Implement `set_webhook(url, secret)` for webhook configuration.<br>4. Implement `get_file(file_id)` for downloading voice notes.<br>5. Parse responses with Pydantic models. |
| **3** | **Formal Interfaces** | **Client (app/clients/telegram.py):**<br>```python<br>import httpx<br>from pydantic import BaseModel<br><br>class TelegramClient:<br>    def __init__(self, bot_token: str):<br>        self.base_url = f"https://api.telegram.org/bot{bot_token}"<br>        self.http = httpx.AsyncClient()<br>    <br>    async def send_message(<br>        self,<br>        chat_id: str,<br>        text: str,<br>        parse_mode: str = "Markdown"<br>    ) -> bool:<br>        response = await self.http.post(<br>            f"{self.base_url}/sendMessage",<br>            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}<br>        )<br>        return response.json()["ok"]<br>    <br>    async def get_file(self, file_id: str) -> bytes:<br>        """Download file by file_id (for voice notes)."""<br>        file_info = await self.http.get(f"{self.base_url}/getFile?file_id={file_id}")<br>        file_path = file_info.json()["result"]["file_path"]<br>        content = await self.http.get(<br>            f"https://api.telegram.org/file/bot{self.token}/{file_path}"<br>        )<br>        return content.content<br>    <br>    async def set_webhook(self, url: str, secret_token: str) -> bool: ...<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send message to valid chat_id, returns True. Invalid chat_id returns False or raises exception. |
| **2** | **Test Logic** | **Given** valid chat_id,<br>**When** `send_message(chat_id, "Hello")`,<br>**Then** returns True and message appears in chat. |
| **3** | **Formal Tests** | Mock httpx responses. Test send_message parses success. Test get_file returns bytes. |

### D. Atomicity Validation

- **Yes.** Client wrapper only.

### E. Dependencies

- INF-005 (Environment configuration for bot token).

---

## INT-005: Resend Client

### A. User Story

> As a **Developer**, I want to **wrap the Resend API** so that sending transactional emails is simple and reliable.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a client for Resend that sends emails with HTML and plain text content. Support templated emails for notifications. Handle delivery errors. |
| **2** | **Logic Flow** | 1. Import Resend SDK.<br>2. Create client with API key.<br>3. Implement `send_email(to, subject, html, text)`.<br>4. Implement template functions for morning/EOD emails.<br>5. Return delivery status. |
| **3** | **Formal Interfaces** | **Client (app/clients/resend.py):**<br>```python<br>import resend<br><br>class ResendClient:<br>    def __init__(self, api_key: str, from_email: str):<br>        resend.api_key = api_key<br>        self.from_email = from_email<br>    <br>    async def send_email(<br>        self,<br>        to: str,<br>        subject: str,<br>        html: str,<br>        text: str | None = None<br>    ) -> str | None:<br>        """Send email, return message ID or None on failure."""<br>        try:<br>            result = resend.Emails.send({<br>                "from": self.from_email,<br>                "to": to,<br>                "subject": subject,<br>                "html": html,<br>                "text": text or html<br>            })<br>            return result["id"]<br>        except Exception as e:<br>            logger.error("Email send failed", error=str(e))<br>            return None<br>```<br><br>**Environment:**<br>```<br>RESEND_API_KEY=re_...<br>RESEND_FROM_EMAIL=noreply@prosthetic.app<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send test email, receive it in inbox. Invalid email returns None instead of crashing. |
| **2** | **Test Logic** | **Given** valid email address,<br>**When** `send_email(to, subject, html)`,<br>**Then** returns message ID string. |
| **3** | **Formal Tests** | Mock Resend SDK. Test returns ID on success. Test returns None on exception. |

### D. Atomicity Validation

- **Yes.** Client wrapper only.

### E. Dependencies

- INF-005 (Environment configuration for API key).

---

## INT-006: Voice Transcription

### A. User Story

> As a **User**, I want to **speak naturally into the app or Telegram** and have my words converted to text accurately.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Unified voice transcription service handling both web audio blobs (MediaRecorder → bytes) and Telegram voice message URLs (file_id → download → bytes). Normalizes input to audio stream for Deepgram. |
| **2** | **Logic Flow** | 1. Accept audio from source (bytes or file_id).<br>2. If Telegram file_id, download via Telegram client.<br>3. Detect format (webm, ogg, mp3).<br>4. Send to Deepgram transcriber.<br>5. Return transcribed text.<br>6. Handle errors (return error message or raise). |
| **3** | **Formal Interfaces** | **Service (app/services/transcription.py):**<br>```python<br>from app.clients.deepgram import DeepgramTranscriber<br>from app.clients.telegram import TelegramClient<br><br>class TranscriptionService:<br>    def __init__(<br>        self,<br>        deepgram: DeepgramTranscriber,<br>        telegram: TelegramClient | None = None<br>    ):<br>        self.deepgram = deepgram<br>        self.telegram = telegram<br>    <br>    async def transcribe_bytes(self, audio: bytes) -> str:<br>        """Transcribe raw audio bytes."""<br>        return await self.deepgram.transcribe(audio)<br>    <br>    async def transcribe_telegram_voice(<br>        self,<br>        file_id: str<br>    ) -> str:<br>        """Download and transcribe Telegram voice note."""<br>        audio = await self.telegram.get_file(file_id)<br>        return await self.deepgram.transcribe(audio)<br>```<br><br>**API Endpoint:**<br>```python<br>@router.post("/transcribe")<br>async def transcribe(audio: UploadFile) -> dict:<br>    text = await transcription_service.transcribe_bytes(await audio.read())<br>    return {"text": text}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Upload 10-second audio saying "Buy milk and call mom." Receive text containing those words with punctuation. |
| **2** | **Test Logic** | **Given** audio file with speech,<br>**When** `transcribe_bytes(audio)`,<br>**Then** returns string containing spoken words. |
| **3** | **Formal Tests** | Integration test with sample audio file. Assert output contains expected keywords. Mock tests for error paths. |

### D. Atomicity Validation

- **Yes.** Orchestrates clients for one purpose.

### E. Dependencies

- INT-003 (Deepgram client).
- INT-004 (Telegram client for voice notes).

---

*End of Integration Specifications*
