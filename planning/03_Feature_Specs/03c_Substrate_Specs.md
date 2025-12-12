# Substrate Feature Specifications

**Category:** SUB (Substrate)
**Total Features:** 13
**Complexity:** 6 Easy, 7 Medium

---

## SUB-001: Database Schema

### A. User Story

> As a **Developer**, I want to **create the complete database schema** so that all application data can be stored and queried efficiently.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create all database tables in Supabase: profiles, actions, conversations, messages, themes, and intent_log. Set up appropriate indexes, constraints, and relationships. Enable required extensions (uuid-ossp). |
| **2** | **Logic Flow** | 1. Enable uuid-ossp extension.<br>2. Create `profiles` table (linked to auth.users).<br>3. Create `actions` table with status enum.<br>4. Create `conversations` table for chat history.<br>5. Create `messages` table for conversation content.<br>6. Create `themes` table for future customization.<br>7. Create indexes on frequently queried columns. |
| **3** | **Formal Interfaces** | **SQL Schema:**<br>```sql<br>-- Extensions<br>CREATE EXTENSION IF NOT EXISTS "uuid-ossp";<br><br>-- Enums<br>CREATE TYPE action_status AS ENUM (<br>  'inbox', 'candidate', 'planned', 'active', 'done', 'dropped', 'rolled'<br>);<br>CREATE TYPE action_complexity AS ENUM ('atomic', 'composite', 'project');<br><br>-- Profiles<br>CREATE TABLE profiles (<br>  id UUID REFERENCES auth.users PRIMARY KEY,<br>  timezone TEXT DEFAULT 'UTC',<br>  telegram_chat_id TEXT UNIQUE,<br>  notification_channel TEXT DEFAULT 'email',<br>  notification_enabled BOOLEAN DEFAULT true,<br>  onboarding_completed BOOLEAN DEFAULT false,<br>  created_at TIMESTAMPTZ DEFAULT NOW(),<br>  updated_at TIMESTAMPTZ DEFAULT NOW()<br>);<br><br>-- Actions (Tasks)<br>CREATE TABLE actions (<br>  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),<br>  user_id UUID REFERENCES auth.users NOT NULL,<br>  parent_id UUID REFERENCES actions(id),<br>  title TEXT NOT NULL,<br>  raw_input TEXT,<br>  status action_status DEFAULT 'inbox',<br>  complexity action_complexity DEFAULT 'atomic',<br>  avoidance_weight INT CHECK (avoidance_weight BETWEEN 1 AND 5) DEFAULT 1,<br>  estimated_minutes INT DEFAULT 15,<br>  actual_minutes INT,<br>  planned_date DATE,<br>  completed_at TIMESTAMPTZ,<br>  position INT DEFAULT 0,<br>  created_at TIMESTAMPTZ DEFAULT NOW(),<br>  updated_at TIMESTAMPTZ DEFAULT NOW()<br>);<br><br>-- Conversations<br>CREATE TABLE conversations (<br>  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),<br>  user_id UUID REFERENCES auth.users NOT NULL,<br>  type TEXT DEFAULT 'capture',  -- 'capture', 'coaching', 'onboarding'<br>  context_action_id UUID REFERENCES actions(id),<br>  created_at TIMESTAMPTZ DEFAULT NOW(),<br>  updated_at TIMESTAMPTZ DEFAULT NOW()<br>);<br><br>-- Messages<br>CREATE TABLE messages (<br>  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),<br>  conversation_id UUID REFERENCES conversations(id) NOT NULL,<br>  role TEXT NOT NULL,  -- 'user', 'assistant', 'system'<br>  content TEXT NOT NULL,<br>  created_at TIMESTAMPTZ DEFAULT NOW()<br>);<br><br>-- Indexes<br>CREATE INDEX idx_actions_user_status ON actions(user_id, status);<br>CREATE INDEX idx_actions_planned_date ON actions(user_id, planned_date);<br>CREATE INDEX idx_messages_conversation ON messages(conversation_id);<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Run migration. All tables exist. Insert test data. Foreign key constraints work. Enum values are enforced. |
| **2** | **Test Logic** | **Given** schema is applied,<br>**When** inserting action with invalid status,<br>**Then** error is raised.<br>**When** inserting action with valid data,<br>**Then** row is created with UUID. |
| **3** | **Formal Tests** | Query `information_schema.tables` for all expected tables. Insert valid row. Insert invalid enum, assert error. |

### D. Atomicity Validation

- **Yes.** Schema definition only.

### E. Dependencies

- INT-001 (Supabase client for execution).

---

## SUB-002: RLS Policies

### A. User Story

> As a **User**, I want my **data to be private** so that no other user can see my actions or conversations.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Enable Row Level Security on all user-owned tables. Create policies that restrict SELECT, INSERT, UPDATE, DELETE to rows where user_id matches the authenticated user. |
| **2** | **Logic Flow** | 1. Enable RLS on profiles, actions, conversations, messages.<br>2. Create policy for each operation type.<br>3. Use `auth.uid()` to get current user.<br>4. For messages, check via conversation ownership.<br>5. Deny all by default. |
| **3** | **Formal Interfaces** | **RLS Policies:**<br>```sql<br>-- Enable RLS<br>ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;<br>ALTER TABLE actions ENABLE ROW LEVEL SECURITY;<br>ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;<br>ALTER TABLE messages ENABLE ROW LEVEL SECURITY;<br><br>-- Profiles: Users can only access their own<br>CREATE POLICY "Users can view own profile"<br>  ON profiles FOR SELECT<br>  USING (auth.uid() = id);<br><br>CREATE POLICY "Users can update own profile"<br>  ON profiles FOR UPDATE<br>  USING (auth.uid() = id);<br><br>-- Actions: Users can only access their own<br>CREATE POLICY "Users can view own actions"<br>  ON actions FOR SELECT<br>  USING (auth.uid() = user_id);<br><br>CREATE POLICY "Users can insert own actions"<br>  ON actions FOR INSERT<br>  WITH CHECK (auth.uid() = user_id);<br><br>CREATE POLICY "Users can update own actions"<br>  ON actions FOR UPDATE<br>  USING (auth.uid() = user_id);<br><br>CREATE POLICY "Users can delete own actions"<br>  ON actions FOR DELETE<br>  USING (auth.uid() = user_id);<br><br>-- Conversations: Users can only access their own<br>CREATE POLICY "Users can manage own conversations"<br>  ON conversations FOR ALL<br>  USING (auth.uid() = user_id);<br><br>-- Messages: Via conversation ownership<br>CREATE POLICY "Users can access messages in own conversations"<br>  ON messages FOR ALL<br>  USING (<br>    EXISTS (<br>      SELECT 1 FROM conversations<br>      WHERE conversations.id = messages.conversation_id<br>      AND conversations.user_id = auth.uid()<br>    )<br>  );<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User A creates an action. User B queries actions. User B's result does not include User A's action. User A can see their own action. |
| **2** | **Test Logic** | **Given** User A is authenticated,<br>**When** selecting from actions,<br>**Then** only User A's actions are returned.<br>**When** User A tries to update User B's action,<br>**Then** 0 rows affected. |
| **3** | **Formal Tests** | Create two users. Insert action for each. Query as User A. Assert count = 1. Assert action.user_id = User A. |

### D. Atomicity Validation

- **Yes.** Security policies only.

### E. Dependencies

- SUB-001 (Tables must exist).

---

## SUB-003: Email/Password Auth

### A. User Story

> As a **User**, I want to **sign up and log in with email/password** so that I can access my account without third-party services.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Enable email/password authentication in Supabase. Create sign-up form that creates user and profile. Create login form that validates credentials and establishes session. Handle password reset flow. |
| **2** | **Logic Flow** | **Sign Up:**<br>1. User enters email + password.<br>2. Call `supabase.auth.signUp({email, password})`.<br>3. Trigger creates profile row.<br>4. Redirect to onboarding.<br><br>**Sign In:**<br>1. User enters credentials.<br>2. Call `supabase.auth.signInWithPassword({email, password})`.<br>3. Session cookie is set.<br>4. Redirect to dashboard. |
| **3** | **Formal Interfaces** | **Auth Functions (lib/auth.ts):**<br>```typescript<br>export async function signUp(email: string, password: string) {<br>  const { data, error } = await supabase.auth.signUp({<br>    email,<br>    password,<br>    options: {<br>      emailRedirectTo: `${location.origin}/auth/callback`<br>    }<br>  })<br>  if (error) throw error<br>  return data<br>}<br><br>export async function signIn(email: string, password: string) {<br>  const { data, error } = await supabase.auth.signInWithPassword({<br>    email,<br>    password<br>  })<br>  if (error) throw error<br>  return data<br>}<br><br>export async function signOut() {<br>  await supabase.auth.signOut()<br>}<br>```<br><br>**Profile Trigger (SQL):**<br>```sql<br>CREATE OR REPLACE FUNCTION handle_new_user()<br>RETURNS TRIGGER AS $$<br>BEGIN<br>  INSERT INTO public.profiles (id)<br>  VALUES (NEW.id);<br>  RETURN NEW;<br>END;<br>$$ LANGUAGE plpgsql SECURITY DEFINER;<br><br>CREATE TRIGGER on_auth_user_created<br>  AFTER INSERT ON auth.users<br>  FOR EACH ROW EXECUTE FUNCTION handle_new_user();<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Sign up with new email. Profile row is created. Sign in with credentials. Session is established. Invalid credentials show error. |
| **2** | **Test Logic** | **Given** valid email and password,<br>**When** signUp is called,<br>**Then** user is created and profile exists.<br>**When** signIn is called,<br>**Then** session is returned. |
| **3** | **Formal Tests** | E2E: Fill sign-up form, submit, verify redirect. Check profiles table has row. Fill login form, submit, verify authenticated state. |

### D. Atomicity Validation

- **Yes.** Authentication flow only.

### E. Dependencies

- SUB-001 (Profiles table).
- INT-001 (Supabase client).

---

## SUB-004: Google OAuth

### A. User Story

> As a **User**, I want to **sign in with Google** so that I can access my account without creating a new password.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Enable Google OAuth in Supabase dashboard. Create "Sign in with Google" button that redirects to Google auth. Handle callback to exchange code for session. Create profile if new user. |
| **2** | **Logic Flow** | 1. User clicks "Sign in with Google".<br>2. Call `supabase.auth.signInWithOAuth({provider: 'google'})`.<br>3. User authenticates with Google.<br>4. Google redirects to callback URL.<br>5. Supabase exchanges code for session.<br>6. Profile trigger creates row if new.<br>7. Redirect to dashboard. |
| **3** | **Formal Interfaces** | **OAuth Function:**<br>```typescript<br>export async function signInWithGoogle() {<br>  const { error } = await supabase.auth.signInWithOAuth({<br>    provider: 'google',<br>    options: {<br>      redirectTo: `${location.origin}/auth/callback`,<br>      queryParams: {<br>        access_type: 'offline',<br>        prompt: 'consent'<br>      }<br>    }<br>  })<br>  if (error) throw error<br>}<br>```<br><br>**Callback Route (app/auth/callback/route.ts):**<br>```typescript<br>import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'<br>import { NextResponse } from 'next/server'<br><br>export async function GET(request: Request) {<br>  const { searchParams } = new URL(request.url)<br>  const code = searchParams.get('code')<br>  <br>  if (code) {<br>    const supabase = createRouteHandlerClient({ cookies })<br>    await supabase.auth.exchangeCodeForSession(code)<br>  }<br>  <br>  return NextResponse.redirect(new URL('/dashboard', request.url))<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Click Google button. Redirect to Google. Authenticate. Return to app logged in. Profile exists. |
| **2** | **Test Logic** | **Given** Google OAuth is configured,<br>**When** signInWithOAuth is called,<br>**Then** browser redirects to Google.<br>**After** Google auth,<br>**Then** callback creates session. |
| **3** | **Formal Tests** | Manual test flow. Verify session cookie exists after callback. Verify profile row created. |

### D. Atomicity Validation

- **Yes.** OAuth flow only.

### E. Dependencies

- SUB-001 (Profiles table).
- SUB-003 (Profile trigger).

---

## SUB-005: Profile Management

### A. User Story

> As a **User**, I want to **update my profile settings** so that the app respects my timezone and notification preferences.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create CRUD operations for user profile. Allow updating timezone, notification channel, and notification enabled status. Provide API endpoint and frontend hooks. |
| **2** | **Logic Flow** | 1. Fetch profile by user_id (from auth).<br>2. Display current values in form.<br>3. User modifies fields.<br>4. PATCH request to update profile.<br>5. Update updated_at timestamp. |
| **3** | **Formal Interfaces** | **API Types:**<br>```typescript<br>interface Profile {<br>  id: string<br>  timezone: string<br>  telegram_chat_id: string | null<br>  notification_channel: 'email' | 'telegram' | 'both'<br>  notification_enabled: boolean<br>  onboarding_completed: boolean<br>}<br><br>interface ProfileUpdate {<br>  timezone?: string<br>  notification_channel?: string<br>  notification_enabled?: boolean<br>}<br>```<br><br>**React Hook:**<br>```typescript<br>export function useProfile() {<br>  const { data, mutate } = useSWR('/api/profile', fetcher)<br>  <br>  const updateProfile = async (updates: ProfileUpdate) => {<br>    await supabase<br>      .from('profiles')<br>      .update(updates)<br>      .eq('id', user.id)<br>    mutate()<br>  }<br>  <br>  return { profile: data, updateProfile }<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Load profile, see current timezone. Change timezone to "America/New_York". Reload page. New timezone persists. |
| **2** | **Test Logic** | **Given** user is authenticated,<br>**When** updateProfile({timezone: "Europe/London"}),<br>**Then** profile.timezone = "Europe/London" on next fetch. |
| **3** | **Formal Tests** | Fetch profile, assert initial values. Update timezone. Fetch again, assert changed. |

### D. Atomicity Validation

- **Yes.** Profile CRUD only.

### E. Dependencies

- SUB-001 (Profiles table).
- SUB-002 (RLS for security).
- SUB-003 (Authentication).

---

## SUB-006: Session Handling

### A. User Story

> As a **User**, I want my **session to persist** across browser closes so I don't have to log in every time.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Configure Supabase session to use secure HTTP-only cookies. Implement token refresh before expiry. Handle session expiry gracefully with redirect to login. |
| **2** | **Logic Flow** | 1. On auth success, Supabase sets session cookie.<br>2. Middleware checks session on protected routes.<br>3. If expired, attempt refresh.<br>4. If refresh fails, redirect to login.<br>5. Refresh token before expiry (background). |
| **3** | **Formal Interfaces** | **Middleware (middleware.ts):**<br>```typescript<br>import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'<br>import { NextResponse } from 'next/server'<br><br>export async function middleware(req: NextRequest) {<br>  const res = NextResponse.next()<br>  const supabase = createMiddlewareClient({ req, res })<br>  <br>  const { data: { session } } = await supabase.auth.getSession()<br>  <br>  // Protected routes<br>  if (req.nextUrl.pathname.startsWith('/dashboard')) {<br>    if (!session) {<br>      return NextResponse.redirect(new URL('/login', req.url))<br>    }<br>  }<br>  <br>  return res<br>}<br><br>export const config = {<br>  matcher: ['/dashboard/:path*', '/settings/:path*']<br>}<br>```<br><br>**Session Refresh Hook:**<br>```typescript<br>useEffect(() => {<br>  const { data: { subscription } } = supabase.auth.onAuthStateChange(<br>    (event, session) => {<br>      if (event === 'TOKEN_REFRESHED') {<br>        // Session refreshed automatically<br>      }<br>      if (event === 'SIGNED_OUT') {<br>        router.push('/login')<br>      }<br>    }<br>  )<br>  return () => subscription.unsubscribe()<br>}, [])<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Log in, close browser, reopen. Still logged in. Let session expire, get redirected to login. |
| **2** | **Test Logic** | **Given** valid session cookie,<br>**When** accessing /dashboard,<br>**Then** allowed.<br>**Given** no session,<br>**Then** redirected to /login. |
| **3** | **Formal Tests** | E2E: Login, verify cookie. Close browser context, reopen, verify still authenticated. Clear cookies, verify redirect. |

### D. Atomicity Validation

- **Yes.** Session middleware only.

### E. Dependencies

- SUB-003 (Authentication must work).

---

## SUB-007: Notification Preferences

### A. User Story

> As a **User**, I want to **control how I receive notifications** so I can choose email, Telegram, or disable them entirely.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Store notification preferences in profile. Options: email, telegram, both, or disabled. UI to toggle each channel. Backend respects preferences when sending. |
| **2** | **Logic Flow** | 1. Profile has `notification_channel` and `notification_enabled` fields.<br>2. Settings UI shows toggles for each option.<br>3. On save, update profile.<br>4. Notification service checks preferences before sending. |
| **3** | **Formal Interfaces** | **Profile Fields:**<br>```sql<br>notification_channel TEXT DEFAULT 'email',  -- 'email', 'telegram', 'both'<br>notification_enabled BOOLEAN DEFAULT true<br>```<br><br>**Settings Component:**<br>```typescript<br>function NotificationSettings({ profile, onUpdate }) {<br>  return (<br>    <div><br>      <Toggle<br>        label="Enable notifications"<br>        checked={profile.notification_enabled}<br>        onChange={(v) => onUpdate({ notification_enabled: v })}<br>      /><br>      <Select<br>        label="Notification channel"<br>        value={profile.notification_channel}<br>        options={['email', 'telegram', 'both']}<br>        onChange={(v) => onUpdate({ notification_channel: v })}<br>        disabled={!profile.notification_enabled}<br>      /><br>    </div><br>  )<br>}<br>```<br><br>**Service Check:**<br>```python<br>async def should_send(user_id: str, channel: str) -> bool:<br>    profile = await get_profile(user_id)<br>    if not profile.notification_enabled:<br>        return False<br>    return channel in profile.notification_channel or profile.notification_channel == 'both'<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Set channel to "telegram". Morning notification goes to Telegram, not email. Disable notifications. No notifications sent. |
| **2** | **Test Logic** | **Given** notification_channel="telegram",<br>**When** sending morning plan,<br>**Then** Telegram receives message, email does not. |
| **3** | **Formal Tests** | Mock notification services. Update preferences. Call notification send. Assert correct service was called. |

### D. Atomicity Validation

- **Yes.** Preference storage and UI only.

### E. Dependencies

- SUB-005 (Profile management).

---

## SUB-008: Timezone Handling

### A. User Story

> As a **User**, I want the **app to respect my timezone** so that "today" means my local day, not UTC.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Store timezone in profile. Auto-detect from browser on first visit. All date operations use user's timezone. Background jobs use timezone to determine local time. |
| **2** | **Logic Flow** | 1. On first visit, detect timezone via `Intl.DateTimeFormat().resolvedOptions().timeZone`.<br>2. Store in profile (or suggest during onboarding).<br>3. Backend queries include timezone conversion.<br>4. Frontend displays dates in local timezone.<br>5. Jobs check "local hour" for scheduling. |
| **3** | **Formal Interfaces** | **Browser Detection:**<br>```typescript<br>const detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone<br>// "America/New_York"<br>```<br><br>**Backend Timezone Utils:**<br>```python<br>from datetime import datetime<br>import pytz<br><br>def get_user_local_time(user_timezone: str) -> datetime:<br>    tz = pytz.timezone(user_timezone)<br>    return datetime.now(tz)<br><br>def get_user_local_hour(user_timezone: str) -> int:<br>    return get_user_local_time(user_timezone).hour<br><br>def is_users_morning(user_timezone: str, target_hour: int = 8) -> bool:<br>    return get_user_local_hour(user_timezone) == target_hour<br>```<br><br>**Date Display:**<br>```typescript<br>function formatDate(date: Date, timezone: string) {<br>  return new Intl.DateTimeFormat('en-US', {<br>    timeZone: timezone,<br>    dateStyle: 'medium',<br>    timeStyle: 'short'<br>  }).format(date)<br>}<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User in Tokyo creates action at 2am Tokyo time. "Today" view shows it for current Tokyo date. User in NYC sees their own "today" correctly. |
| **2** | **Test Logic** | **Given** user timezone="Asia/Tokyo",<br>**When** getting "today's actions" at 2am Tokyo,<br>**Then** returns actions with planned_date = Tokyo's current date. |
| **3** | **Formal Tests** | Mock datetime. Set timezone. Call `is_users_morning`. Assert True at 8am local, False at 9am. |

### D. Atomicity Validation

- **Yes.** Timezone utilities only.

### E. Dependencies

- SUB-005 (Profile stores timezone).

---

## SUB-009: Job: State Transitions

### A. User Story

> As a **System**, I want to **automatically transition action states** at the start of each day so users wake up to a fresh "today" view.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a scheduled job that runs hourly. For each user whose local time is 4am, transition any actions that are still "planned" or "active" back to "inbox" (or "rolled" state). This ensures yesterday's unfinished work doesn't clutter today. |
| **2** | **Logic Flow** | 1. Job runs every hour via Railway cron.<br>2. Query users where local time = 4am.<br>3. For each user, find actions with status IN ('planned', 'active').<br>4. Update status to 'rolled'.<br>5. Log transition count. |
| **3** | **Formal Interfaces** | **Job Script (jobs/state_transitions.py):**<br>```python<br>import asyncio<br>from app.clients.supabase import supabase<br>from app.utils.timezone import get_users_at_local_hour<br><br>async def run_state_transitions():<br>    # Get users at 4am local time<br>    users = await get_users_at_local_hour(4)<br>    <br>    for user in users:<br>        result = supabase.table('actions').update({<br>            'status': 'rolled',<br>            'planned_date': None<br>        }).eq('user_id', user['id']).in_(<br>            'status', ['planned', 'active']<br>        ).execute()<br>        <br>        logger.info(<br>            "State transition complete",<br>            user_id=user['id'],<br>            rolled_count=len(result.data)<br>        )<br><br>if __name__ == "__main__":<br>    asyncio.run(run_state_transitions())<br>```<br><br>**Cron Config:**<br>```<br>0 * * * *  python jobs/state_transitions.py<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User has 3 "planned" actions at midnight. At 4am their time, job runs. Actions are now "rolled" with no planned_date. |
| **2** | **Test Logic** | **Given** user with timezone at 4am and 2 planned actions,<br>**When** job runs,<br>**Then** both actions have status='rolled'. |
| **3** | **Formal Tests** | Insert test actions. Mock time to 4am. Run job. Query actions. Assert status changed. |

### D. Atomicity Validation

- **Yes.** Single job logic.

### E. Dependencies

- SUB-001 (Actions table).
- SUB-008 (Timezone handling).

---

## SUB-010: Job: Morning Plan

### A. User Story

> As a **User**, I want to **wake up to a plan suggestion** so I don't have to decide what to do from scratch.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a scheduled job that runs hourly. For each user whose local time is 8am, generate a suggested plan from their inbox (top 3 items by avoidance weight). Send notification via their preferred channel. |
| **2** | **Logic Flow** | 1. Job runs every hour.<br>2. Query users where local time = 8am AND notifications enabled.<br>3. For each user, get top 3 inbox items (ORDER BY avoidance_weight DESC, created_at ASC).<br>4. Update these to 'candidate' status.<br>5. Format message with suggestions.<br>6. Send via notification gateway (respects channel preference). |
| **3** | **Formal Interfaces** | **Job Script (jobs/morning_plan.py):**<br>```python<br>async def run_morning_plan():<br>    users = await get_users_at_local_hour(8)<br>    <br>    for user in users:<br>        if not user['notification_enabled']:<br>            continue<br>        <br>        # Get top inbox items<br>        actions = supabase.table('actions').select('*').eq(<br>            'user_id', user['id']<br>        ).eq('status', 'inbox').order(<br>            'avoidance_weight', desc=True<br>        ).order('created_at').limit(3).execute()<br>        <br>        if not actions.data:<br>            continue<br>        <br>        # Mark as candidates<br>        ids = [a['id'] for a in actions.data]<br>        supabase.table('actions').update({<br>            'status': 'candidate'<br>        }).in_('id', ids).execute()<br>        <br>        # Send notification<br>        message = format_morning_message(actions.data)<br>        await notify_user(user, message)<br>```<br><br>**Message Format:**<br>```<br>Good morning! Here are today's suggested wins:<br><br>• Do taxes (~60m) - High impact!<br>• Reply to Sarah (~15m)<br>• Buy groceries (~30m)<br><br>Ready to commit? Open the app to start your day.<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User has 5 inbox items. At 8am their time, they receive notification with top 3 suggestions. Those 3 are now "candidate" status. |
| **2** | **Test Logic** | **Given** user at 8am with 5 inbox items,<br>**When** job runs,<br>**Then** notification sent with 3 items.<br>**Then** 3 actions have status='candidate'. |
| **3** | **Formal Tests** | Mock time. Insert 5 inbox actions. Run job. Verify notify called. Verify 3 status changes. |

### D. Atomicity Validation

- **Yes.** Single job logic.

### E. Dependencies

- SUB-001 (Actions table).
- SUB-007 (Notification preferences).
- SUB-008 (Timezone handling).
- NTF-001 (Notification gateway).

---

## SUB-011: Job: EOD Summary

### A. User Story

> As a **User**, I want to **receive an end-of-day summary** so I can celebrate wins and close out my day with intention.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a scheduled job that runs hourly. For each user whose local time is 8pm, generate a day summary highlighting completed actions (especially high-avoidance wins). Send notification via preferred channel. |
| **2** | **Logic Flow** | 1. Job runs every hour.<br>2. Query users where local time = 20:00 (8pm) AND notifications enabled.<br>3. For each user, get today's completed actions.<br>4. Identify high-avoidance wins (weight >= 4).<br>5. Call AI to generate encouraging summary.<br>6. Send via notification gateway. |
| **3** | **Formal Interfaces** | **Job Script (jobs/eod_summary.py):**<br>```python<br>async def run_eod_summary():<br>    users = await get_users_at_local_hour(20)<br>    <br>    for user in users:<br>        if not user['notification_enabled']:<br>            continue<br>        <br>        # Get today's completed actions<br>        today = get_user_today(user['timezone'])<br>        actions = supabase.table('actions').select('*').eq(<br>            'user_id', user['id']<br>        ).eq('status', 'done').gte(<br>            'completed_at', today<br>        ).execute()<br>        <br>        if not actions.data:<br>            message = "No tasks completed today, but tomorrow is a fresh start!"<br>        else:<br>            message = await generate_eod_summary(actions.data)<br>        <br>        await notify_user(user, message)<br>```<br><br>**Summary Message:**<br>```<br>Great day! You completed 4 tasks.<br><br>Highlight: You tackled "Do taxes" - that was a big one!<br><br>Take a breath. You did real work today.<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User completes 3 tasks including a high-avoidance one. At 8pm, they receive summary highlighting the hard win. |
| **2** | **Test Logic** | **Given** user at 8pm with 3 done actions (1 high-avoidance),<br>**When** job runs,<br>**Then** notification mentions the high-avoidance task name. |
| **3** | **Formal Tests** | Insert completed actions with varying weights. Mock AI response. Run job. Verify notification content. |

### D. Atomicity Validation

- **Yes.** Single job logic.

### E. Dependencies

- SUB-001 (Actions table).
- SUB-007 (Notification preferences).
- SUB-008 (Timezone handling).
- NTF-001 (Notification gateway).
- INT-002 (Claude API Client - for summary generation).

**Note:** Summary generation uses a simple prompt via INT-002 directly, not a dedicated AGT feature. If summary logic becomes complex, extract to AGT-017.

---

## SUB-012: Job: Inactivity Check

### A. User Story

> As a **User**, I want to **receive a gentle check-in** if I haven't used the app in 3+ days so I don't fall off completely.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Create a scheduled job that runs daily. Find users who haven't created any actions or messages in the last 3 days. Send a gentle, non-shaming check-in message. Don't send if notifications are disabled. |
| **2** | **Logic Flow** | 1. Job runs daily at noon UTC.<br>2. Query users with no activity in 3+ days.<br>3. Filter to those with notifications enabled.<br>4. Send gentle check-in message.<br>5. Log who was contacted. |
| **3** | **Formal Interfaces** | **Job Script (jobs/inactivity_check.py):**<br>```python<br>async def run_inactivity_check():<br>    three_days_ago = datetime.now(UTC) - timedelta(days=3)<br>    <br>    # Find inactive users<br>    inactive_users = supabase.rpc('get_inactive_users', {<br>        'since': three_days_ago.isoformat()<br>    }).execute()<br>    <br>    for user in inactive_users.data:<br>        if not user['notification_enabled']:<br>            continue<br>        <br>        message = (<br>            "Hey! Just checking in. No pressure - "<br>            "when you're ready, I'm here to help you capture "<br>            "what's on your mind. One small thing at a time."<br>        )<br>        await notify_user(user, message)<br>        <br>        logger.info("Inactivity check sent", user_id=user['id'])<br>```<br><br>**Database Function:**<br>```sql<br>CREATE OR REPLACE FUNCTION get_inactive_users(since TIMESTAMPTZ)<br>RETURNS SETOF profiles AS $$<br>  SELECT p.* FROM profiles p<br>  WHERE p.notification_enabled = true<br>  AND NOT EXISTS (<br>    SELECT 1 FROM actions a<br>    WHERE a.user_id = p.id AND a.created_at > since<br>  )<br>  AND NOT EXISTS (<br>    SELECT 1 FROM messages m<br>    JOIN conversations c ON c.id = m.conversation_id<br>    WHERE c.user_id = p.id AND m.created_at > since AND m.role = 'user'<br>  )<br>$$ LANGUAGE sql;<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User hasn't opened app in 4 days. They receive gentle check-in. User active yesterday receives nothing. |
| **2** | **Test Logic** | **Given** user with last activity 4 days ago,<br>**When** job runs,<br>**Then** notification sent.<br>**Given** user active yesterday,<br>**Then** no notification. |
| **3** | **Formal Tests** | Insert users with various last activity dates. Run job. Verify only 3+ day inactive users are contacted. |

### D. Atomicity Validation

- **Yes.** Single job logic.

### E. Dependencies

- SUB-001 (Tables for activity check).
- SUB-007 (Notification preferences).
- NTF-001 (Notification gateway).

---

## SUB-013: Real-time Subscriptions

### A. User Story

> As a **User**, I want to **see updates instantly** when actions are modified (e.g., from Telegram) without refreshing the page.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Set up Supabase real-time subscriptions for the actions table. When any action for the current user is inserted, updated, or deleted, update the frontend state immediately. |
| **2** | **Logic Flow** | 1. On component mount, subscribe to actions table changes.<br>2. Filter by user_id (via RLS).<br>3. On INSERT: add to local state.<br>4. On UPDATE: update in local state.<br>5. On DELETE: remove from local state.<br>6. Cleanup subscription on unmount. |
| **3** | **Formal Interfaces** | **React Hook (hooks/useRealtimeActions.ts):**<br>```typescript<br>export function useRealtimeActions(initialActions: Action[]) {<br>  const [actions, setActions] = useState(initialActions)<br>  <br>  useEffect(() => {<br>    const channel = supabase<br>      .channel('actions-changes')<br>      .on(<br>        'postgres_changes',<br>        {<br>          event: '*',<br>          schema: 'public',<br>          table: 'actions'<br>        },<br>        (payload) => {<br>          if (payload.eventType === 'INSERT') {<br>            setActions(prev => [...prev, payload.new as Action])<br>          } else if (payload.eventType === 'UPDATE') {<br>            setActions(prev => prev.map(a => <br>              a.id === payload.new.id ? payload.new as Action : a<br>            ))<br>          } else if (payload.eventType === 'DELETE') {<br>            setActions(prev => prev.filter(a => a.id !== payload.old.id))<br>          }<br>        }<br>      )<br>      .subscribe()<br>    <br>    return () => {<br>      supabase.removeChannel(channel)<br>    }<br>  }, [])<br>  <br>  return actions<br>}<br>```<br><br>**Supabase Config (Enable Realtime):**<br>```sql<br>ALTER TABLE actions REPLICA IDENTITY FULL;<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Open app in two tabs. Create action in tab 1. Tab 2 shows new action without refresh. |
| **2** | **Test Logic** | **Given** subscription is active,<br>**When** action is inserted via another source,<br>**Then** local state updates within 1 second. |
| **3** | **Formal Tests** | E2E: Open two browser contexts. Insert action in one. Verify appears in other. Measure latency < 2 seconds. |

### D. Atomicity Validation

- **Yes.** Subscription logic only.

### E. Dependencies

- SUB-001 (Actions table with REPLICA IDENTITY).
- INT-001 (Supabase client).

---

*End of Substrate Specifications*
