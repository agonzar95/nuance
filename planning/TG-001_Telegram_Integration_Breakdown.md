# TG-001: Telegram Integration - Implementation Breakdown

**Parent Feature:** TG-001 Telegram Integration
**Complexity:** Hard
**Total Substeps:** 6
**Dependencies:** NTF-003, NTF-004, NTF-005, NTF-006, INT-004, INF-010

---

## Overview

The Telegram integration is partially complete. The bot can send/receive messages, but users cannot connect their Telegram account to their Nuance profile. This breakdown covers the complete account linking flow.

### Current State
- Bot sends/receives messages ✓
- Commands work (/start, /help, /today, /status) ✓
- Settings page shows connection status ✓
- **Missing:** Actual account linking flow

### Target State
- User sends `/start` to bot → receives link with token
- User clicks link → frontend validates token → account linked
- User can disconnect from settings

---

## Substep Breakdown

### TG-0011: Database Migration - Pending Connections Table

**Purpose:** Create a table to store temporary connection tokens with expiration.

**Implementation:**
- Create migration file: `backend/supabase/migrations/005_telegram_connections.sql`
- Table: `pending_telegram_connections`
- Columns:
  - `id` (uuid, primary key)
  - `token` (text, unique, indexed)
  - `telegram_chat_id` (text, not null)
  - `expires_at` (timestamptz, not null)
  - `created_at` (timestamptz, default now())

**Success Criteria:**
| Criterion | Validation |
|-----------|------------|
| Migration runs | `supabase db push` succeeds without errors |
| Table exists | Query `SELECT * FROM pending_telegram_connections` returns empty result (not error) |
| Token is indexed | `\d pending_telegram_connections` shows index on token column |
| Expiration queryable | `SELECT * FROM pending_telegram_connections WHERE expires_at > now()` works |

**Artifacts:**
- `backend/supabase/migrations/005_telegram_connections.sql`

**Dependencies:** None

---

### TG-0012: Backend Service - Token Storage

**Purpose:** Service layer for creating, validating, and consuming connection tokens.

**Implementation:**
- Create: `backend/app/services/telegram_connection.py`
- Class: `TelegramConnectionService`
- Methods:
  - `create_token(chat_id: str) -> str` - Generate token, store with 15-min expiry, return token
  - `validate_token(token: str) -> str | None` - Return chat_id if valid and not expired, else None
  - `consume_token(token: str) -> str | None` - Validate and delete token, return chat_id
  - `cleanup_expired() -> int` - Delete expired tokens, return count

**Success Criteria:**
| Criterion | Validation |
|-----------|------------|
| Token created | `create_token("123")` returns 43-char URL-safe string |
| Token stored | After create, row exists in `pending_telegram_connections` |
| Token expires | Token created with `expires_at` = now + 15 minutes |
| Valid token returns chat_id | `validate_token(token)` returns "123" |
| Expired token returns None | Token with past expiry returns None |
| Consume deletes token | After `consume_token()`, token no longer in DB |
| Cleanup works | `cleanup_expired()` removes old tokens |

**Artifacts:**
- `backend/app/services/telegram_connection.py`

**Dependencies:** TG-0011

---

### TG-0013: Update /start Command - Store Tokens

**Purpose:** Modify the `/start` command to actually persist tokens using the new service.

**Implementation:**
- Update: `backend/app/services/notifications/telegram/commands.py`
- Changes:
  - Import `TelegramConnectionService`
  - Replace `_generate_connection_token()` to use service
  - Remove TODO comments

**Success Criteria:**
| Criterion | Validation |
|-----------|------------|
| Token persisted | After `/start`, token exists in `pending_telegram_connections` |
| Correct chat_id | Stored token has correct `telegram_chat_id` |
| Link in message | Bot response contains `/settings/telegram?token=...` |
| Existing user skips token | Connected users get "Welcome back" without new token |

**Test Flow:**
1. Send `/start` to bot from unconnected Telegram account
2. Receive message with connection link
3. Query DB: `SELECT * FROM pending_telegram_connections WHERE telegram_chat_id = '<chat_id>'`
4. Verify token exists and expires_at is ~15 min in future

**Artifacts:**
- Updated `backend/app/services/notifications/telegram/commands.py`

**Dependencies:** TG-0012

---

### TG-0014: Backend API - Connection Endpoint

**Purpose:** Authenticated endpoint to validate token and link Telegram to user profile.

**Implementation:**
- Create: `backend/app/routers/telegram_connect.py` (or add to existing `telegram.py`)
- Endpoint: `POST /api/telegram/connect`
- Request body: `{ "token": "..." }`
- Logic:
  1. Verify user is authenticated (JWT)
  2. Consume token via `TelegramConnectionService`
  3. If valid, update user's profile `telegram_chat_id`
  4. Return success/error response
- Also add: `POST /api/telegram/disconnect`
  - Clear `telegram_chat_id` from profile

**Success Criteria:**
| Criterion | Validation |
|-----------|------------|
| Auth required | Request without JWT returns 401 |
| Invalid token | Non-existent token returns 400 with error message |
| Expired token | Expired token returns 400 with "Token expired" |
| Valid token links | Profile updated with `telegram_chat_id` |
| Token consumed | After success, same token returns 400 |
| Disconnect works | `POST /disconnect` clears `telegram_chat_id` |

**Test Flow:**
1. Create token via `/start` command
2. `POST /api/telegram/connect` with token + valid JWT
3. Verify response is 200 OK
4. Query profile: `telegram_chat_id` matches original chat_id
5. Token no longer in `pending_telegram_connections`

**Artifacts:**
- `backend/app/routers/telegram_connect.py` (or updated `telegram.py`)
- Updated `backend/app/main.py` (register router)

**Dependencies:** TG-0012

---

### TG-0015: Frontend - Connection Page

**Purpose:** Page that handles the connection link from Telegram and completes the flow.

**Implementation:**
- Create: `frontend/src/app/(app)/settings/telegram/page.tsx`
- URL: `/settings/telegram?token=<token>`
- Flow:
  1. Extract `token` from URL params
  2. If no token, redirect to `/dashboard/settings`
  3. Show loading state
  4. Call `POST /api/telegram/connect` with token
  5. On success: Show success message, redirect to settings after 2s
  6. On error: Show error message with "Try Again" (re-do /start)
- Also add API client method: `connectTelegram(token: string)`

**Success Criteria:**
| Criterion | Validation |
|-----------|------------|
| Page loads | `/settings/telegram?token=abc` renders without error |
| No token redirects | `/settings/telegram` (no token) redirects to settings |
| Loading shown | Spinner displayed while API call in progress |
| Success flow | Valid token shows "Connected!" message |
| Redirect after success | Auto-redirects to `/dashboard/settings` after 2 seconds |
| Error shown | Invalid token shows error message |
| Retry guidance | Error state tells user to send `/start` again |
| Auth required | Unauthenticated users redirected to login |

**Test Flow:**
1. Get connection link from Telegram `/start`
2. Open link in browser (logged into Nuance)
3. See loading → success message
4. Redirected to settings
5. Settings shows "Connected" status

**Artifacts:**
- `frontend/src/app/(app)/settings/telegram/page.tsx`
- Updated `frontend/src/lib/api.ts` (add `connectTelegram` method)

**Dependencies:** TG-0014

---

### TG-0016: Frontend - Disconnect Functionality

**Purpose:** Allow users to unlink their Telegram account from settings.

**Implementation:**
- Update: `frontend/src/app/(app)/dashboard/settings/page.tsx`
- Changes:
  - Add "Disconnect" button when Telegram is connected
  - Confirmation dialog before disconnect
  - Call `POST /api/telegram/disconnect`
  - Update UI on success
- Add API client method: `disconnectTelegram()`

**Success Criteria:**
| Criterion | Validation |
|-----------|------------|
| Button visible | "Disconnect" button shown when connected |
| Confirmation | Clicking shows "Are you sure?" dialog |
| Cancel works | Dismissing dialog does nothing |
| Disconnect works | Confirming clears connection |
| UI updates | Settings immediately shows "Not connected" state |
| Can reconnect | After disconnect, can do /start flow again |

**Test Flow:**
1. Go to settings (with Telegram connected)
2. Click "Disconnect Telegram"
3. Confirm in dialog
4. See "Not connected" status
5. Send `/start` in Telegram
6. Complete connection flow again

**Artifacts:**
- Updated `frontend/src/app/(app)/dashboard/settings/page.tsx`
- Updated `frontend/src/lib/api.ts` (add `disconnectTelegram` method)

**Dependencies:** TG-0014

---

## Implementation Order

```
TG-0011 (Migration)
    ↓
TG-0012 (Token Service)
    ↓
TG-0013 (Update /start)
    ↓
TG-0014 (API Endpoint)
    ↓
┌───┴───┐
↓       ↓
TG-0015  TG-0016
(Connect Page)  (Disconnect UI)
```

**Recommended sequence:**
1. TG-0011 → TG-0012 → TG-0013 (Backend foundation)
2. TG-0014 (API layer)
3. TG-0015 → TG-0016 (Frontend, can be parallel)

---

## End-to-End Validation

After all substeps complete, verify the full flow:

### Happy Path
1. User logs into Nuance web app
2. User opens Telegram, searches for @NuanceBot
3. User sends `/start`
4. Bot responds with connection link
5. User clicks link
6. Page shows "Connecting..." then "Connected!"
7. User redirected to settings
8. Settings shows green "Connected" status
9. User sends "Buy groceries" to bot
10. Task appears in Nuance inbox

### Disconnect Path
1. User goes to settings
2. Clicks "Disconnect Telegram"
3. Confirms in dialog
4. Status changes to "Not connected"
5. Sending messages to bot now prompts for `/start`

### Error Paths
- Expired token (>15 min): Shows "Token expired, please send /start again"
- Invalid token: Shows "Invalid token"
- Already connected: `/start` says "Welcome back!" (no new token)
- Network error: Shows retry option

---

## Commit Strategy

Each substep should be committed separately:

```
[TG-0011] Add pending_telegram_connections migration
[TG-0012] Add TelegramConnectionService for token management
[TG-0013] Update /start command to persist connection tokens
[TG-0014] Add /api/telegram/connect and /disconnect endpoints
[TG-0015] Add Telegram connection page
[TG-0016] Add Telegram disconnect functionality to settings
```

Final rollup commit (optional):
```
[TG-001] Complete Telegram account linking integration
```

---

*Created: December 17, 2025*
