# Notification Feature Specifications

**Category:** NTF (Notification Layer)
**Total Features:** 9
**Complexity:** 7 Easy, 2 Medium, 0 Hard

---

## NTF-001: Gateway Abstraction

### A. User Story

> As a **Developer**, I want to **use a unified notification interface** so that I can send messages through any channel without knowing the implementation details.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Abstract gateway interface for all notification channels. Single method to send regardless of channel. Handles routing based on user preferences. Returns delivery status. |
| **2** | **Logic Flow** | 1. Receive notification request with user and content.<br>2. Look up user's preferred channel.<br>3. Route to appropriate provider (email/telegram).<br>4. Provider sends message.<br>5. Return success/failure status. |
| **3** | **Formal Interfaces** | **NotificationGateway (services/notifications/gateway.py):**<br>```python<br>from abc import ABC, abstractmethod<br>from enum import Enum<br>from dataclasses import dataclass<br>from typing import Optional<br><br><br>class NotificationChannel(Enum):<br>    EMAIL = "email"<br>    TELEGRAM = "telegram"<br><br><br>class NotificationType(Enum):<br>    MORNING_PLAN = "morning_plan"<br>    EOD_SUMMARY = "eod_summary"<br>    INACTIVITY_CHECK = "inactivity_check"<br>    CUSTOM = "custom"<br><br><br>@dataclass<br>class NotificationPayload:<br>    user_id: str<br>    notification_type: NotificationType<br>    subject: Optional[str] = None<br>    body: str = ""<br>    data: Optional[dict] = None<br><br><br>@dataclass<br>class DeliveryResult:<br>    success: bool<br>    channel: NotificationChannel<br>    provider_id: Optional[str] = None<br>    error: Optional[str] = None<br><br><br>class NotificationProvider(ABC):<br>    @abstractmethod<br>    async def send(self, user_id: str, payload: NotificationPayload) -> DeliveryResult:<br>        pass<br><br><br>class NotificationGateway:<br>    def __init__(<br>        self,<br>        email_provider: NotificationProvider,<br>        telegram_provider: NotificationProvider,<br>        user_service: UserService<br>    ):<br>        self.providers = {<br>            NotificationChannel.EMAIL: email_provider,<br>            NotificationChannel.TELEGRAM: telegram_provider<br>        }<br>        self.user_service = user_service<br><br>    async def send(<br>        self,<br>        payload: NotificationPayload<br>    ) -> DeliveryResult:<br>        # Get user's preferred channel<br>        preferences = await self.user_service.get_notification_preferences(<br>            payload.user_id<br>        )<br>        channel = preferences.preferred_channel<br>        <br>        # Route to provider<br>        provider = self.providers.get(channel)<br>        if not provider:<br>            return DeliveryResult(<br>                success=False,<br>                channel=channel,<br>                error=f"No provider for channel: {channel}"<br>            )<br>        <br>        try:<br>            result = await provider.send(payload.user_id, payload)<br>            return result<br>        except Exception as e:<br>            return DeliveryResult(<br>                success=False,<br>                channel=channel,<br>                error=str(e)<br>            )<br>```<br><br>**Usage:**<br>```python<br>gateway = NotificationGateway(<br>    email_provider=ResendEmailProvider(api_key),<br>    telegram_provider=TelegramProvider(bot_token),<br>    user_service=user_service<br>)<br><br>result = await gateway.send(NotificationPayload(<br>    user_id="user_123",<br>    notification_type=NotificationType.MORNING_PLAN,<br>    subject="Your plan for today",<br>    body="Here are your top priorities..."<br>))<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send notification. Gateway checks user preference. Routes to correct provider. Returns delivery result. |
| **2** | **Test Logic** | **Given** user prefers Telegram,<br>**When** notification sent,<br>**Then** Telegram provider called.<br>**Given** user prefers email,<br>**Then** email provider called. |
| **3** | **Formal Tests** | Mock providers. Set user preference. Send notification. Verify correct provider called. Check result. |

### D. Atomicity Validation

- **Yes.** Gateway abstraction only.

### E. Dependencies

- NTF-002 (Email client).
- NTF-004 (Telegram send).
- NTF-009 (Channel router).
- SUB-007 (Notification preferences).

---

## NTF-002: Email Client (Resend)

### A. User Story

> As the **System**, I want to **send emails via Resend** so that users can receive notifications in their inbox.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Resend API wrapper implementing NotificationProvider. Formats content for email. Includes retry logic with exponential backoff (3 retries). Returns delivery status with message ID. |
| **2** | **Logic Flow** | 1. Receive notification payload.<br>2. Get user's email address.<br>3. Format subject and body for email.<br>4. Call Resend API with retry (max 3, exponential backoff).<br>5. Return result with message ID or error after all retries exhausted. |
| **3** | **Formal Interfaces** | **ResendEmailProvider (services/notifications/providers/email.py):**<br>```python<br>import resend<br>from typing import Optional<br><br><br>class ResendEmailProvider(NotificationProvider):<br>    def __init__(<br>        self,<br>        api_key: str,<br>        from_email: str,<br>        user_service: UserService<br>    ):<br>        resend.api_key = api_key<br>        self.from_email = from_email<br>        self.user_service = user_service<br><br>    async def send(<br>        self,<br>        user_id: str,<br>        payload: NotificationPayload<br>    ) -> DeliveryResult:<br>        # Get user email<br>        user = await self.user_service.get_user(user_id)<br>        if not user or not user.email:<br>            return DeliveryResult(<br>                success=False,<br>                channel=NotificationChannel.EMAIL,<br>                error="User email not found"<br>            )<br>        <br>        # Format content<br>        subject = payload.subject or self._default_subject(payload.notification_type)<br>        html_body = self._format_html(payload)<br>        <br>        try:<br>            response = resend.Emails.send({<br>                "from": self.from_email,<br>                "to": user.email,<br>                "subject": subject,<br>                "html": html_body<br>            })<br>            <br>            return DeliveryResult(<br>                success=True,<br>                channel=NotificationChannel.EMAIL,<br>                provider_id=response["id"]<br>            )<br>        except Exception as e:<br>            return DeliveryResult(<br>                success=False,<br>                channel=NotificationChannel.EMAIL,<br>                error=str(e)<br>            )<br><br>    def _default_subject(self, notification_type: NotificationType) -> str:<br>        subjects = {<br>            NotificationType.MORNING_PLAN: "Your plan for today",<br>            NotificationType.EOD_SUMMARY: "Your day in review",<br>            NotificationType.INACTIVITY_CHECK: "We miss you!",<br>        }<br>        return subjects.get(notification_type, "Notification")<br><br>    def _format_html(self, payload: NotificationPayload) -> str:<br>        return f"""<br>        <!DOCTYPE html><br>        <html><br>        <head><br>            <style><br>                body {{ font-family: system-ui, sans-serif; line-height: 1.6; color: #333; }}<br>                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}<br>                .footer {{ margin-top: 40px; font-size: 12px; color: #666; }}<br>            </style><br>        </head><br>        <body><br>            <div class="container"><br>                {payload.body}<br>                <div class="footer"><br>                    <p>Sent from your Executive Function Prosthetic</p><br>                </div><br>            </div><br>        </body><br>        </html><br>        """<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send email notification. Resend API called with user's email. Success returns message ID. |
| **2** | **Test Logic** | **Given** valid user email,<br>**When** send called,<br>**Then** Resend API called with correct params.<br>**Then** result has provider_id. |
| **3** | **Formal Tests** | Mock Resend API. Send notification. Verify API called. Verify response parsed. Test error handling. |

### D. Atomicity Validation

- **Yes.** Resend email provider only.

### E. Dependencies

- INT-005 (Resend client).

**Note:** Inline retry with exponential backoff (3 retries, 2^attempt seconds delay). For persistent failures, consider adding NTF-010 (Delivery Retry Queue) post-MVP.

---

## NTF-003: Telegram Bot Setup

### A. User Story

> As a **Developer**, I want to **configure the Telegram bot** so that users can interact with the system via Telegram.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Bot registration with BotFather. Webhook configuration for receiving messages. Environment-based configuration. Health check for bot connectivity. |
| **2** | **Logic Flow** | 1. Load bot token from environment.<br>2. Initialize bot client.<br>3. Register webhook URL.<br>4. Verify webhook is receiving.<br>5. Handle webhook updates. |
| **3** | **Formal Interfaces** | **TelegramBotSetup (services/notifications/telegram/setup.py):**<br>```python<br>import httpx<br>from typing import Optional<br>import logging<br><br>logger = logging.getLogger(__name__)<br><br><br>class TelegramBotConfig:<br>    def __init__(self, bot_token: str, webhook_url: str):<br>        self.bot_token = bot_token<br>        self.webhook_url = webhook_url<br>        self.api_base = f"https://api.telegram.org/bot{bot_token}"<br><br><br>class TelegramBotSetup:<br>    def __init__(self, config: TelegramBotConfig):<br>        self.config = config<br>        self.client = httpx.AsyncClient(timeout=30.0)<br><br>    async def setup_webhook(self) -> bool:<br>        """Register webhook with Telegram"""<br>        try:<br>            response = await self.client.post(<br>                f"{self.config.api_base}/setWebhook",<br>                json={<br>                    "url": self.config.webhook_url,<br>                    "allowed_updates": ["message", "callback_query"]<br>                }<br>            )<br>            data = response.json()<br>            <br>            if data.get("ok"):<br>                logger.info(f"Webhook set to {self.config.webhook_url}")<br>                return True<br>            else:<br>                logger.error(f"Webhook setup failed: {data}")<br>                return False<br>        except Exception as e:<br>            logger.error(f"Webhook setup error: {e}")<br>            return False<br><br>    async def get_webhook_info(self) -> Optional[dict]:<br>        """Check current webhook status"""<br>        try:<br>            response = await self.client.get(<br>                f"{self.config.api_base}/getWebhookInfo"<br>            )<br>            data = response.json()<br>            return data.get("result")<br>        except Exception as e:<br>            logger.error(f"Get webhook info error: {e}")<br>            return None<br><br>    async def verify_bot(self) -> Optional[dict]:<br>        """Verify bot token is valid"""<br>        try:<br>            response = await self.client.get(<br>                f"{self.config.api_base}/getMe"<br>            )<br>            data = response.json()<br>            if data.get("ok"):<br>                return data.get("result")<br>            return None<br>        except Exception as e:<br>            logger.error(f"Bot verification error: {e}")<br>            return None<br><br>    async def delete_webhook(self) -> bool:<br>        """Remove webhook (for local dev with polling)"""<br>        try:<br>            response = await self.client.post(<br>                f"{self.config.api_base}/deleteWebhook"<br>            )<br>            return response.json().get("ok", False)<br>        except Exception:<br>            return False<br>```<br><br>**FastAPI Webhook Endpoint:**<br>```python<br>from fastapi import APIRouter, Request, HTTPException<br><br>router = APIRouter()<br><br>@router.post("/telegram/webhook")<br>async def telegram_webhook(request: Request):<br>    try:<br>        update = await request.json()<br>        await telegram_handler.process_update(update)<br>        return {"ok": True}<br>    except Exception as e:<br>        logger.error(f"Webhook error: {e}")<br>        raise HTTPException(status_code=500)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Start app. Bot verified. Webhook registered. Telegram messages received at endpoint. |
| **2** | **Test Logic** | **Given** valid bot token,<br>**When** verify_bot called,<br>**Then** returns bot info.<br>**When** setup_webhook called,<br>**Then** returns True. |
| **3** | **Formal Tests** | Mock Telegram API. Test verify_bot. Test setup_webhook. Test webhook endpoint receives updates. |

### D. Atomicity Validation

- **Yes.** Bot setup and webhook configuration only.

### E. Dependencies

- INT-004 (Telegram API client).
- INF-005 (Environment config).

---

## NTF-004: Telegram Send

### A. User Story

> As the **System**, I want to **send messages to users via Telegram** so that they receive notifications in their chat.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send message to user's Telegram chat. Format content appropriately. Handle rate limits. Support Markdown formatting. Return delivery status. |
| **2** | **Logic Flow** | 1. Get user's Telegram chat ID.<br>2. Format message content.<br>3. Call sendMessage API.<br>4. Handle errors (blocked, rate limit).<br>5. Return result. |
| **3** | **Formal Interfaces** | **TelegramProvider (services/notifications/providers/telegram.py):**<br>```python<br>import httpx<br>from typing import Optional<br><br><br>class TelegramProvider(NotificationProvider):<br>    def __init__(self, bot_token: str, user_service: UserService):<br>        self.api_base = f"https://api.telegram.org/bot{bot_token}"<br>        self.user_service = user_service<br>        self.client = httpx.AsyncClient(timeout=30.0)<br><br>    async def send(<br>        self,<br>        user_id: str,<br>        payload: NotificationPayload<br>    ) -> DeliveryResult:<br>        # Get user's Telegram chat ID<br>        user = await self.user_service.get_user(user_id)<br>        chat_id = user.telegram_chat_id if user else None<br>        <br>        if not chat_id:<br>            return DeliveryResult(<br>                success=False,<br>                channel=NotificationChannel.TELEGRAM,<br>                error="User Telegram not connected"<br>            )<br>        <br>        # Format message<br>        text = self._format_message(payload)<br>        <br>        return await self.send_message(chat_id, text)<br><br>    async def send_message(<br>        self,<br>        chat_id: str,<br>        text: str,<br>        parse_mode: str = "Markdown"<br>    ) -> DeliveryResult:<br>        try:<br>            response = await self.client.post(<br>                f"{self.api_base}/sendMessage",<br>                json={<br>                    "chat_id": chat_id,<br>                    "text": text,<br>                    "parse_mode": parse_mode<br>                }<br>            )<br>            data = response.json()<br>            <br>            if data.get("ok"):<br>                return DeliveryResult(<br>                    success=True,<br>                    channel=NotificationChannel.TELEGRAM,<br>                    provider_id=str(data["result"]["message_id"])<br>                )<br>            else:<br>                return DeliveryResult(<br>                    success=False,<br>                    channel=NotificationChannel.TELEGRAM,<br>                    error=data.get("description", "Unknown error")<br>                )<br>        except Exception as e:<br>            return DeliveryResult(<br>                success=False,<br>                channel=NotificationChannel.TELEGRAM,<br>                error=str(e)<br>            )<br><br>    def _format_message(self, payload: NotificationPayload) -> str:<br>        if payload.notification_type == NotificationType.MORNING_PLAN:<br>            return self._format_morning_plan(payload)<br>        elif payload.notification_type == NotificationType.EOD_SUMMARY:<br>            return self._format_eod_summary(payload)<br>        else:<br>            return payload.body<br><br>    def _format_morning_plan(self, payload: NotificationPayload) -> str:<br>        header = "*Good morning!* Here's your plan:\n\n"<br>        tasks = payload.data.get("tasks", []) if payload.data else []<br>        task_list = "\n".join([f"• {t}" for t in tasks])<br>        return header + task_list<br><br>    def _format_eod_summary(self, payload: NotificationPayload) -> str:<br>        return f"*Day Summary*\n\n{payload.body}"<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send Telegram notification. User receives message in chat. Message formatted with Markdown. |
| **2** | **Test Logic** | **Given** user with chat_id,<br>**When** send called,<br>**Then** sendMessage API called.<br>**Then** result has message_id. |
| **3** | **Formal Tests** | Mock Telegram API. Send message. Verify API called with correct chat_id. Test formatting. Test error cases. |

### D. Atomicity Validation

- **Yes.** Telegram send functionality only.

### E. Dependencies

- NTF-003 (Telegram bot setup).
- INT-004 (Telegram API client).

---

## NTF-005: Telegram Receive

### A. User Story

> As the **System**, I want to **receive and process Telegram messages** so that users can interact with the system via chat.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Webhook receives Telegram updates. Parse message content (text or voice). Identify user by chat ID. Route to extraction pipeline. Save actions to database. |
| **2** | **Logic Flow** | 1. Webhook receives update.<br>2. If voice message, transcribe via INT-006.<br>3. Extract message text and chat ID.<br>4. Look up user by chat ID.<br>5. If unknown, prompt to connect account.<br>6. If known, call AGT-016 for extraction.<br>7. Save action to database.<br>8. Send confirmation. |
| **3** | **Formal Interfaces** | **TelegramHandler (services/notifications/telegram/handler.py):**<br>```python<br>from dataclasses import dataclass<br>from typing import Optional<br>import logging<br><br>logger = logging.getLogger(__name__)<br><br><br>@dataclass<br>class TelegramUpdate:<br>    update_id: int<br>    message_id: Optional[int]<br>    chat_id: str<br>    text: Optional[str]<br>    from_user: Optional[dict]<br><br><br>class TelegramHandler:<br>    def __init__(<br>        self,<br>        user_service: UserService,<br>        capture_service: CaptureService,<br>        telegram_provider: TelegramProvider<br>    ):<br>        self.user_service = user_service<br>        self.capture_service = capture_service<br>        self.telegram = telegram_provider<br><br>    async def process_update(self, raw_update: dict):<br>        """Process incoming Telegram update"""<br>        update = self._parse_update(raw_update)<br>        if not update or not update.text:<br>            return<br>        <br>        # Check for commands<br>        if update.text.startswith("/"):<br>            await self._handle_command(update)<br>            return<br>        <br>        # Look up user<br>        user = await self.user_service.get_user_by_telegram(update.chat_id)<br>        <br>        if not user:<br>            # Unknown user - prompt to connect<br>            await self.telegram.send_message(<br>                update.chat_id,<br>                "I don't recognize you yet! Please connect your account at [app URL]"<br>            )<br>            return<br>        <br>        # Process as capture input<br>        try:<br>            result = await self.capture_service.process_input(<br>                user_id=user.id,<br>                text=update.text,<br>                source="telegram"<br>            )<br>            <br>            # Send confirmation<br>            if result.action:<br>                await self.telegram.send_message(<br>                    update.chat_id,<br>                    f"Got it! Added: *{result.action.title}*"<br>                )<br>        except Exception as e:<br>            logger.error(f"Capture error: {e}")<br>            await self.telegram.send_message(<br>                update.chat_id,<br>                "Sorry, I couldn't process that. Try again?"<br>            )<br><br>    def _parse_update(self, raw: dict) -> Optional[TelegramUpdate]:<br>        message = raw.get("message", {})<br>        if not message:<br>            return None<br>        <br>        return TelegramUpdate(<br>            update_id=raw.get("update_id"),<br>            message_id=message.get("message_id"),<br>            chat_id=str(message.get("chat", {}).get("id")),<br>            text=message.get("text"),<br>            from_user=message.get("from")<br>        )<br><br>    async def _handle_command(self, update: TelegramUpdate):<br>        """Route to command handler"""<br>        # Implemented in NTF-006<br>        pass<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User sends message in Telegram. System receives via webhook. Identifies user. Processes as capture. Sends confirmation. |
| **2** | **Test Logic** | **Given** message from known user,<br>**When** processed,<br>**Then** capture_service called.<br>**Then** confirmation sent.<br>**Given** unknown user,<br>**Then** connect prompt sent. |
| **3** | **Formal Tests** | Mock services. Process update from known user. Verify capture called. Process from unknown. Verify prompt sent. |

### D. Atomicity Validation

- **Yes.** Telegram message receiving only.

### E. Dependencies

- NTF-003 (Telegram bot setup).
- NTF-004 (Telegram send for responses).
- AGT-016 (Extraction Orchestrator for processing input).
- INT-006 (Voice Transcription - for voice messages).

---

## NTF-006: Telegram Commands

### A. User Story

> As a **User**, I want to **use Telegram commands** so that I can quickly interact with the system.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Handle /start, /help, /today, /status commands. Provide quick information and guidance. Connect new users. Show help text. |
| **2** | **Logic Flow** | 1. Parse command from message.<br>2. /start → show welcome, link to connect.<br>3. /help → show available commands.<br>4. /today → show today's plan.<br>5. /status → show current progress. |
| **3** | **Formal Interfaces** | **TelegramCommandHandler (services/notifications/telegram/commands.py):**<br>```python<br>from typing import Callable, Dict, Awaitable<br><br><br>class TelegramCommandHandler:<br>    def __init__(<br>        self,<br>        telegram: TelegramProvider,<br>        user_service: UserService,<br>        planning_service: PlanningService<br>    ):<br>        self.telegram = telegram<br>        self.user_service = user_service<br>        self.planning_service = planning_service<br>        <br>        self.commands: Dict[str, Callable] = {<br>            "/start": self.cmd_start,<br>            "/help": self.cmd_help,<br>            "/today": self.cmd_today,<br>            "/status": self.cmd_status,<br>        }<br><br>    async def handle(self, update: TelegramUpdate) -> bool:<br>        """Handle command, return True if handled"""<br>        if not update.text or not update.text.startswith("/"):<br>            return False<br>        <br>        command = update.text.split()[0].lower()<br>        handler = self.commands.get(command)<br>        <br>        if handler:<br>            await handler(update)<br>            return True<br>        <br>        return False<br><br>    async def cmd_start(self, update: TelegramUpdate):<br>        """Welcome message and connection link"""<br>        user = await self.user_service.get_user_by_telegram(update.chat_id)<br>        <br>        if user:<br>            await self.telegram.send_message(<br>                update.chat_id,<br>                f"Welcome back! You're connected as {user.email}.\n\n"<br>                "Just send me what's on your mind and I'll capture it."<br>            )<br>        else:<br>            # Generate connection token<br>            token = await self.user_service.generate_telegram_token(update.chat_id)<br>            link = f"https://app.example.com/connect/telegram?token={token}"<br>            <br>            await self.telegram.send_message(<br>                update.chat_id,<br>                f"*Welcome to your Executive Function Prosthetic!*\n\n"<br>                f"To get started, connect your account:\n{link}"<br>            )<br><br>    async def cmd_help(self, update: TelegramUpdate):<br>        """Show available commands"""<br>        help_text = """<br>*Available Commands*<br><br>/start - Connect or check your account<br>/today - See today's plan<br>/status - See your current progress<br>/help - Show this message<br><br>Or just send me a message to capture a task!<br>        """<br>        await self.telegram.send_message(update.chat_id, help_text.strip())<br><br>    async def cmd_today(self, update: TelegramUpdate):<br>        """Show today's plan"""<br>        user = await self.user_service.get_user_by_telegram(update.chat_id)<br>        if not user:<br>            await self.telegram.send_message(<br>                update.chat_id,<br>                "Please connect your account first with /start"<br>            )<br>            return<br>        <br>        plan = await self.planning_service.get_today(user.id)<br>        <br>        if not plan or not plan.actions:<br>            await self.telegram.send_message(<br>                update.chat_id,<br>                "No plan set for today yet. Open the app to plan your day!"<br>            )<br>            return<br>        <br>        tasks = "\n".join([<br>            f"{'✓' if a.status == 'done' else '○'} {a.title}"<br>            for a in plan.actions<br>        ])<br>        await self.telegram.send_message(<br>            update.chat_id,<br>            f"*Today's Plan*\n\n{tasks}"<br>        )<br><br>    async def cmd_status(self, update: TelegramUpdate):<br>        """Show progress status"""<br>        user = await self.user_service.get_user_by_telegram(update.chat_id)<br>        if not user:<br>            await self.telegram.send_message(<br>                update.chat_id,<br>                "Please connect your account first with /start"<br>            )<br>            return<br>        <br>        stats = await self.planning_service.get_today_stats(user.id)<br>        <br>        await self.telegram.send_message(<br>            update.chat_id,<br>            f"*Today's Progress*\n\n"<br>            f"Completed: {stats.completed}/{stats.total}\n"<br>            f"Time spent: {stats.minutes_spent} min"<br>        )<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Send /help. Receive command list. Send /today. See plan. Send /status. See progress. |
| **2** | **Test Logic** | **Given** /help sent,<br>**Then** help text returned.<br>**Given** /today from connected user,<br>**Then** plan displayed. |
| **3** | **Formal Tests** | Send each command. Verify correct response. Test with connected vs unconnected user. |

### D. Atomicity Validation

- **Yes.** Telegram command handling only.

### E. Dependencies

- NTF-004 (Telegram send).
- NTF-005 (Telegram receive).

---

## NTF-007: Morning Plan Content

### A. User Story

> As the **System**, I want to **format morning plan notifications** so that users receive clear, actionable daily plans.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Generate formatted content for morning plan notification. Include top tasks, time estimates, and motivation. Adapt format for email vs Telegram. |
| **2** | **Logic Flow** | 1. Receive plan data (actions, estimates).<br>2. Generate greeting based on time.<br>3. List prioritized tasks.<br>4. Include total time estimate.<br>5. Add motivational element.<br>6. Format for target channel. |
| **3** | **Formal Interfaces** | **MorningPlanContent (services/notifications/content/morning.py):**<br>```python<br>from dataclasses import dataclass<br>from typing import List<br>from datetime import date<br><br><br>@dataclass<br>class PlanTask:<br>    title: str<br>    estimated_minutes: int<br>    avoidance_weight: int<br><br><br>@dataclass<br>class MorningPlanData:<br>    date: date<br>    tasks: List[PlanTask]<br>    total_minutes: int<br><br><br>class MorningPlanContent:<br>    def format_email(self, data: MorningPlanData) -> tuple[str, str]:<br>        """Returns (subject, html_body)"""<br>        subject = f"Your plan for {data.date.strftime('%A, %B %d')}"<br>        <br>        task_html = ""<br>        for task in data.tasks:<br>            dots = "●" * task.avoidance_weight + "○" * (5 - task.avoidance_weight)<br>            task_html += f"""<br>            <tr><br>                <td style="padding: 12px; border-bottom: 1px solid #eee;"><br>                    <strong>{task.title}</strong><br>                    <br><small style="color: #666;">~{task.estimated_minutes} min</small><br>                </td><br>                <td style="padding: 12px; text-align: right; font-size: 10px;">{dots}</td><br>            </tr><br>            """<br>        <br>        hours = data.total_minutes // 60<br>        mins = data.total_minutes % 60<br>        time_str = f"{hours}h {mins}m" if hours else f"{mins}m"<br>        <br>        body = f"""<br>        <h2 style="margin-bottom: 20px;">Good morning!</h2><br>        <p>Here's what's on your plate today:</p><br>        <br>        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;"><br>            {task_html}<br>        </table><br>        <br>        <p style="color: #666;"><br>            Total planned time: <strong>{time_str}</strong><br>        </p><br>        <br>        <p style="margin-top: 30px;"><br>            <a href="https://app.example.com/today" <br>               style="background: #4F46E5; color: white; padding: 12px 24px; <br>                      text-decoration: none; border-radius: 6px;"><br>                Open Today View<br>            </a><br>        </p><br>        """<br>        <br>        return subject, body<br><br>    def format_telegram(self, data: MorningPlanData) -> str:<br>        """Returns formatted Telegram message"""<br>        day_name = data.date.strftime("%A")<br>        <br>        task_lines = []<br>        for task in data.tasks:<br>            dots = "●" * task.avoidance_weight<br>            task_lines.append(f"• {task.title} (~{task.estimated_minutes}min) {dots}")<br>        <br>        tasks_str = "\n".join(task_lines)<br>        <br>        hours = data.total_minutes // 60<br>        mins = data.total_minutes % 60<br>        time_str = f"{hours}h {mins}m" if hours else f"{mins}m"<br>        <br>        return f"""<br>*Good morning!* Happy {day_name}.<br><br>Here's your plan for today:<br><br>{tasks_str}<br><br>Total: {time_str}<br><br>You've got this.<br>        """.strip()<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Format plan with 3 tasks. Email has HTML table. Telegram has bullet list. Both show time total. |
| **2** | **Test Logic** | **Given** 3 tasks totaling 90 minutes,<br>**Then** email shows "1h 30m".<br>**Then** Telegram shows "1h 30m".<br>**Then** all tasks listed. |
| **3** | **Formal Tests** | Format with mock data. Verify email structure. Verify Telegram format. Check time calculations. |

### D. Atomicity Validation

- **Yes.** Morning content formatting only.

### E. Dependencies

- SUB-010 (Job: Morning plan generation).

---

## NTF-008: EOD Summary Content

### A. User Story

> As the **System**, I want to **format end-of-day summary notifications** so that users can review their day.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Generate formatted content for EOD notification. Include completed tasks, remaining count, highlights. Supportive tone regardless of completion rate. |
| **2** | **Logic Flow** | 1. Receive day data (completed, remaining, wins).<br>2. Celebrate completions.<br>3. Highlight high-avoidance wins.<br>4. Mention remaining without judgment.<br>5. Include AI summary if available.<br>6. Format for channel. |
| **3** | **Formal Interfaces** | **EODSummaryContent (services/notifications/content/eod.py):**<br>```python<br>from dataclasses import dataclass<br>from typing import List, Optional<br>from datetime import date<br><br><br>@dataclass<br>class CompletedTask:<br>    title: str<br>    avoidance_weight: int<br><br><br>@dataclass<br>class EODSummaryData:<br>    date: date<br>    completed: List[CompletedTask]<br>    remaining_count: int<br>    high_avoidance_wins: List[str]<br>    ai_summary: Optional[str]<br><br><br>class EODSummaryContent:<br>    def format_email(self, data: EODSummaryData) -> tuple[str, str]:<br>        """Returns (subject, html_body)"""<br>        completed_count = len(data.completed)<br>        subject = f"Your day: {completed_count} tasks completed"<br>        <br>        # Completed section<br>        completed_html = ""<br>        for task in data.completed:<br>            completed_html += f"<li style='margin: 8px 0;'>✓ {task.title}</li>"<br>        <br>        # Wins section<br>        wins_html = ""<br>        if data.high_avoidance_wins:<br>            wins_html = """<br>            <div style="background: #FEF3C7; padding: 16px; border-radius: 8px; margin: 20px 0;"><br>                <strong>⭐ Today's Wins</strong><br>                <p style="margin: 8px 0 0 0;">You pushed through things you'd been avoiding:</p><br>                <ul style="margin: 8px 0; padding-left: 20px;"><br>            """<br>            for win in data.high_avoidance_wins:<br>                wins_html += f"<li>{win}</li>"<br>            wins_html += "</ul></div>"<br>        <br>        # Remaining note<br>        remaining_html = ""<br>        if data.remaining_count > 0:<br>            remaining_html = f"""<br>            <p style="color: #666; margin-top: 20px;"><br>                {data.remaining_count} tasks rolled to tomorrow. That's okay - tomorrow is a new day.<br>            </p><br>            """<br>        <br>        # AI Summary<br>        summary_html = ""<br>        if data.ai_summary:<br>            summary_html = f"""<br>            <div style="background: #F3F4F6; padding: 16px; border-radius: 8px; margin: 20px 0; font-style: italic;"><br>                {data.ai_summary}<br>            </div><br>            """<br>        <br>        body = f"""<br>        <h2>Day Complete</h2><br>        <br>        {wins_html}<br>        <br>        <h3>Completed Today ({completed_count})</h3><br>        <ul style="padding-left: 20px;">{completed_html}</ul><br>        <br>        {summary_html}<br>        {remaining_html}<br>        <br>        <p style="margin-top: 30px;">Rest well. See you tomorrow.</p><br>        """<br>        <br>        return subject, body<br><br>    def format_telegram(self, data: EODSummaryData) -> str:<br>        """Returns formatted Telegram message"""<br>        completed_count = len(data.completed)<br>        <br>        lines = [f"*Day Complete* - {completed_count} tasks done"]<br>        <br>        # Wins<br>        if data.high_avoidance_wins:<br>            lines.append("")<br>            lines.append("⭐ *Wins*")<br>            for win in data.high_avoidance_wins:<br>                lines.append(f"  {win}")<br>        <br>        # Completed<br>        lines.append("")<br>        lines.append("*Completed:*")<br>        for task in data.completed[:5]:  # Limit for readability<br>            lines.append(f"✓ {task.title}")<br>        if len(data.completed) > 5:<br>            lines.append(f"  ...and {len(data.completed) - 5} more")<br>        <br>        # Summary<br>        if data.ai_summary:<br>            lines.append("")<br>            lines.append(f"_{data.ai_summary}_")<br>        <br>        # Remaining<br>        if data.remaining_count > 0:<br>            lines.append("")<br>            lines.append(f"{data.remaining_count} tasks rolled to tomorrow.")<br>        <br>        lines.append("")<br>        lines.append("Rest well.")<br>        <br>        return "\n".join(lines)<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Format summary with 5 completed, 2 remaining, 1 win. Email shows wins highlighted. Telegram shows wins section. Remaining mentioned gently. |
| **2** | **Test Logic** | **Given** 5 completed and 2 wins,<br>**Then** email shows wins block.<br>**Then** Telegram shows ⭐ section.<br>**Given** 3 remaining,<br>**Then** "3 tasks rolled" shown. |
| **3** | **Formal Tests** | Format with various data. Verify wins display. Verify remaining message. Test empty cases. |

### D. Atomicity Validation

- **Yes.** EOD content formatting only.

### E. Dependencies

- SUB-011 (Job: EOD Summary generation).

---

## NTF-009: Channel Router

### A. User Story

> As the **System**, I want to **route notifications to the user's preferred channel** so that they receive messages where they want them.

### B. Implementation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | Look up user's notification preferences. Determine appropriate channel based on notification type and preferences. Fall back to available channel if preferred unavailable. |
| **2** | **Logic Flow** | 1. Load user notification preferences.<br>2. Check notification type.<br>3. Get preferred channel for type.<br>4. Verify channel is configured (has email/chat_id).<br>5. Fall back if needed.<br>6. Return channel to use. |
| **3** | **Formal Interfaces** | **ChannelRouter (services/notifications/router.py):**<br>```python<br>from dataclasses import dataclass<br>from typing import Optional<br>from enum import Enum<br><br><br>class NotificationChannel(Enum):<br>    EMAIL = "email"<br>    TELEGRAM = "telegram"<br><br><br>@dataclass<br>class NotificationPreferences:<br>    morning_plan: NotificationChannel<br>    eod_summary: NotificationChannel<br>    inactivity_check: NotificationChannel<br>    default: NotificationChannel<br>    email_enabled: bool<br>    telegram_enabled: bool<br><br><br>@dataclass<br>class UserChannelConfig:<br>    email: Optional[str]<br>    telegram_chat_id: Optional[str]<br><br><br>class ChannelRouter:<br>    def __init__(self, user_service: UserService):<br>        self.user_service = user_service<br><br>    async def get_channel(<br>        self,<br>        user_id: str,<br>        notification_type: NotificationType<br>    ) -> Optional[NotificationChannel]:<br>        """Determine which channel to use for notification"""<br>        <br>        # Get user preferences and config<br>        prefs = await self.user_service.get_notification_preferences(user_id)<br>        config = await self.user_service.get_channel_config(user_id)<br>        <br>        if not prefs:<br>            return self._get_default_channel(config)<br>        <br>        # Get preferred channel for this type<br>        preferred = self._get_preferred_channel(prefs, notification_type)<br>        <br>        # Check if preferred channel is available<br>        if self._is_channel_available(preferred, config, prefs):<br>            return preferred<br>        <br>        # Fall back to other available channel<br>        return self._get_fallback_channel(preferred, config, prefs)<br><br>    def _get_preferred_channel(<br>        self,<br>        prefs: NotificationPreferences,<br>        notification_type: NotificationType<br>    ) -> NotificationChannel:<br>        channel_map = {<br>            NotificationType.MORNING_PLAN: prefs.morning_plan,<br>            NotificationType.EOD_SUMMARY: prefs.eod_summary,<br>            NotificationType.INACTIVITY_CHECK: prefs.inactivity_check,<br>        }<br>        return channel_map.get(notification_type, prefs.default)<br><br>    def _is_channel_available(<br>        self,<br>        channel: NotificationChannel,<br>        config: UserChannelConfig,<br>        prefs: NotificationPreferences<br>    ) -> bool:<br>        if channel == NotificationChannel.EMAIL:<br>            return bool(config.email) and prefs.email_enabled<br>        elif channel == NotificationChannel.TELEGRAM:<br>            return bool(config.telegram_chat_id) and prefs.telegram_enabled<br>        return False<br><br>    def _get_fallback_channel(<br>        self,<br>        preferred: NotificationChannel,<br>        config: UserChannelConfig,<br>        prefs: NotificationPreferences<br>    ) -> Optional[NotificationChannel]:<br>        # Try the other channel<br>        if preferred == NotificationChannel.TELEGRAM:<br>            if self._is_channel_available(NotificationChannel.EMAIL, config, prefs):<br>                return NotificationChannel.EMAIL<br>        else:<br>            if self._is_channel_available(NotificationChannel.TELEGRAM, config, prefs):<br>                return NotificationChannel.TELEGRAM<br>        <br>        return None<br><br>    def _get_default_channel(<br>        self,<br>        config: UserChannelConfig<br>    ) -> Optional[NotificationChannel]:<br>        # Default preference order: email first<br>        if config.email:<br>            return NotificationChannel.EMAIL<br>        elif config.telegram_chat_id:<br>            return NotificationChannel.TELEGRAM<br>        return None<br>``` |

### C. Validation Contracts

| Level | Format | Description |
|-------|--------|-------------|
| **1** | **Plain English** | User prefers Telegram for morning plan. Has Telegram connected. Router returns Telegram. Telegram disconnected. Falls back to email. |
| **2** | **Test Logic** | **Given** user prefers Telegram and has chat_id,<br>**Then** returns TELEGRAM.<br>**Given** prefers Telegram but no chat_id,<br>**Then** returns EMAIL fallback. |
| **3** | **Formal Tests** | Mock preferences. Test preferred available. Test preferred unavailable. Test no channels available. |

### D. Atomicity Validation

- **Yes.** Channel routing logic only.

### E. Dependencies

- SUB-007 (Notification preferences).

**Note:** NTF-001 (Gateway) uses this router; this feature does not depend on the gateway.

---

*End of Notification Specifications*
