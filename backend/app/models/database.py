"""Database models for Nuance - matches SUB-001 schema.

These Pydantic models represent the database tables and provide
type-safe interfaces for database operations.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    """Status of an action/task."""

    INBOX = "inbox"          # Captured but not reviewed
    CANDIDATE = "candidate"  # Suggested for today (morning plan)
    PLANNED = "planned"      # Committed to today's plan
    ACTIVE = "active"        # Currently being worked on
    DONE = "done"            # Completed
    DROPPED = "dropped"      # User decided not to do
    ROLLED = "rolled"        # Rolled over from previous day


class ActionComplexity(str, Enum):
    """Complexity level of an action."""

    ATOMIC = "atomic"        # Single focused action (<30 min)
    COMPOSITE = "composite"  # Multi-step but manageable (30-120 min)
    PROJECT = "project"      # Needs breakdown (>2 hours)


class ConversationType(str, Enum):
    """Type of conversation."""

    CAPTURE = "capture"      # Task capture session
    COACHING = "coaching"    # Emotional support / stuck
    ONBOARDING = "onboarding"  # New user onboarding


class MessageRole(str, Enum):
    """Role of message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class NotificationChannel(str, Enum):
    """Notification delivery channel."""

    EMAIL = "email"
    TELEGRAM = "telegram"
    BOTH = "both"


# Base models with common fields
class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Profile models
class ProfileBase(BaseModel):
    """Base profile data."""

    timezone: str = "UTC"
    telegram_chat_id: Optional[str] = None
    notification_channel: NotificationChannel = NotificationChannel.EMAIL
    notification_enabled: bool = True
    onboarding_completed: bool = False


class ProfileCreate(ProfileBase):
    """Data for creating a profile (auto-created on signup)."""

    pass


class ProfileUpdate(BaseModel):
    """Data for updating a profile."""

    timezone: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    notification_channel: Optional[NotificationChannel] = None
    notification_enabled: Optional[bool] = None
    onboarding_completed: Optional[bool] = None


class Profile(ProfileBase, TimestampMixin):
    """Full profile model as stored in database."""

    id: UUID


# Action models
class ActionBase(BaseModel):
    """Base action data."""

    title: str = Field(..., min_length=1, max_length=500)
    raw_input: Optional[str] = None
    status: ActionStatus = ActionStatus.INBOX
    complexity: ActionComplexity = ActionComplexity.ATOMIC
    avoidance_weight: int = Field(default=1, ge=1, le=5)
    estimated_minutes: int = Field(default=15, ge=5, le=480)
    actual_minutes: Optional[int] = Field(default=None, ge=0)
    planned_date: Optional[date] = None
    position: int = 0


class ActionCreate(ActionBase):
    """Data for creating an action."""

    parent_id: Optional[UUID] = None


class ActionUpdate(BaseModel):
    """Data for updating an action."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    status: Optional[ActionStatus] = None
    complexity: Optional[ActionComplexity] = None
    avoidance_weight: Optional[int] = Field(default=None, ge=1, le=5)
    estimated_minutes: Optional[int] = Field(default=None, ge=5, le=480)
    actual_minutes: Optional[int] = Field(default=None, ge=0)
    planned_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    position: Optional[int] = None


class Action(ActionBase, TimestampMixin):
    """Full action model as stored in database."""

    id: UUID
    user_id: UUID
    parent_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None


# Conversation models
class ConversationBase(BaseModel):
    """Base conversation data."""

    type: ConversationType = ConversationType.CAPTURE
    context_action_id: Optional[UUID] = None


class ConversationCreate(ConversationBase):
    """Data for creating a conversation."""

    pass


class Conversation(ConversationBase, TimestampMixin):
    """Full conversation model as stored in database."""

    id: UUID
    user_id: UUID


# Message models
class MessageBase(BaseModel):
    """Base message data."""

    role: MessageRole
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Data for creating a message."""

    conversation_id: UUID


class Message(MessageBase):
    """Full message model as stored in database."""

    id: UUID
    conversation_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)


# Token usage models (for AGT-005)
class TokenUsageCreate(BaseModel):
    """Data for recording token usage."""

    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    endpoint: Optional[str] = None


class TokenUsage(TokenUsageCreate):
    """Full token usage record."""

    id: UUID
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def total_tokens(self) -> int:
        """Total tokens used in this request."""
        return self.input_tokens + self.output_tokens


# API Response models
class ActionResponse(Action):
    """Action model for API responses."""

    class Config:
        from_attributes = True


class ProfileResponse(Profile):
    """Profile model for API responses."""

    class Config:
        from_attributes = True
