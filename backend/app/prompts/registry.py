"""Prompt versioning and registry.

Provides versioned prompts for AI operations. Each prompt has a name,
version, and content. The registry tracks active versions and supports
A/B testing of prompt variations.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class PromptVersion:
    """A versioned prompt template."""

    name: str
    version: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def format(self, **kwargs: Any) -> str:
        """Format the prompt with given variables.

        Args:
            **kwargs: Variables to substitute in the prompt.

        Returns:
            Formatted prompt string.
        """
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            logger.warning(
                "Missing prompt variable",
                prompt=self.name,
                version=self.version,
                missing_key=str(e),
            )
            return self.content


class PromptRegistry:
    """Registry for versioned prompts.

    Manages prompt versions and provides lookup by name.
    Supports multiple versions per prompt for A/B testing.
    """

    def __init__(self) -> None:
        """Initialize the registry with default prompts."""
        self._prompts: dict[str, PromptVersion] = {}
        self._all_versions: dict[str, list[PromptVersion]] = {}
        self._load_default_prompts()

    def register(self, prompt: PromptVersion) -> None:
        """Register a prompt version.

        Args:
            prompt: The prompt version to register.
        """
        # Store in all versions list
        if prompt.name not in self._all_versions:
            self._all_versions[prompt.name] = []
        self._all_versions[prompt.name].append(prompt)

        # Set as active if marked active
        if prompt.is_active:
            self._prompts[prompt.name] = prompt
            logger.debug(
                "Prompt registered",
                name=prompt.name,
                version=prompt.version,
            )

    def get(self, name: str) -> PromptVersion:
        """Get the active prompt by name.

        Args:
            name: The prompt name.

        Returns:
            The active PromptVersion.

        Raises:
            KeyError: If prompt not found.
        """
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found in registry")
        return self._prompts[name]

    def get_version(self, name: str, version: str) -> PromptVersion | None:
        """Get a specific version of a prompt.

        Args:
            name: The prompt name.
            version: The version string.

        Returns:
            The PromptVersion or None if not found.
        """
        if name not in self._all_versions:
            return None

        for prompt in self._all_versions[name]:
            if prompt.version == version:
                return prompt
        return None

    def list_prompts(self) -> list[str]:
        """List all registered prompt names."""
        return list(self._prompts.keys())

    def list_versions(self, name: str) -> list[str]:
        """List all versions of a prompt.

        Args:
            name: The prompt name.

        Returns:
            List of version strings.
        """
        if name not in self._all_versions:
            return []
        return [p.version for p in self._all_versions[name]]

    def _load_default_prompts(self) -> None:
        """Load the default set of prompts."""
        # Extraction prompt (AGT-008)
        self.register(PromptVersion(
            name="extraction",
            version="1.0.0",
            content="""You are an executive function assistant helping extract actionable tasks.

Given the user's input, identify distinct tasks and extract them as structured actions.

Rules:
- Each task should be concrete and actionable
- Estimate time in minutes (round to 15-minute increments)
- If input is vague, create a reasonable interpretation
- Multiple tasks in one sentence should be split
- Preserve the user's language where possible

Examples:
"I need to call mom and buy groceries" → 2 actions
"That big report thing" → 1 action: "Work on report"
""",
            metadata={"category": "extraction"},
        ))

        # Avoidance detection prompt (AGT-009)
        self.register(PromptVersion(
            name="avoidance",
            version="1.0.0",
            content="""Analyze the emotional resistance in this task description.

Score from 1-5:
1 = Neutral/easy task, no resistance signals
2 = Mild reluctance or minor annoyance
3 = Moderate avoidance, some emotional weight
4 = Significant resistance, dread language
5 = High avoidance, fear or strong negative emotion

Signals to look for:
- Explicit dread: "ugh", "hate", "dreading"
- Anxiety markers: "finally", "have to", "should have"
- Avoidance history: "been putting off", "keep forgetting"
- Emotional load: "scary", "overwhelming", "huge"
- Minimization: "just need to", "only have to" (often masks difficulty)

Be calibrated: most tasks are 1-2. Reserve 4-5 for genuine emotional difficulty.
""",
            metadata={"category": "extraction"},
        ))

        # Complexity classification prompt (AGT-010)
        self.register(PromptVersion(
            name="complexity",
            version="1.0.0",
            content="""Classify this task's complexity for someone with executive function challenges.

ATOMIC: Can be done in one focused session without decisions
- "Send email to John"
- "Buy milk"
- "Call mom"

COMPOSITE: Has clear sub-steps but is still one task
- "Clean kitchen" (dishes, counters, floor)
- "Prepare presentation" (outline, slides, practice)

PROJECT: Requires planning, research, or multiple sessions
- "Do taxes"
- "Plan vacation"
- "Learn Python"

Err on the side of COMPOSITE for borderline cases - better to offer breakdown.
""",
            metadata={"category": "extraction"},
        ))

        # Breakdown prompt (AGT-012)
        self.register(PromptVersion(
            name="breakdown",
            version="1.0.0",
            content="""You are an executive function coach helping someone who is paralyzed by a task.

Break this task into 3-5 MICRO-STEPS that are:
1. PHYSICAL - involve body movement, not just thinking
2. IMMEDIATE - can start right now with no preparation
3. TINY - each takes 2-10 minutes maximum
4. SEQUENTIAL - ordered by what comes first

Focus on INITIATION - the hardest part is starting.

BAD steps: "Research options", "Think about approach", "Plan the project"
GOOD steps: "Open laptop", "Create new document", "Write one sentence"

Example - "Clean kitchen":
1. Walk to kitchen sink (1 min)
2. Put dishes in dishwasher (5 min)
3. Wipe one counter (3 min)
4. Sweep floor in front of stove (5 min)
5. Take out trash bag (2 min)

Example - "Do taxes":
1. Open filing cabinet drawer (1 min)
2. Pull out W-2 forms (2 min)
3. Open TurboTax website (1 min)
4. Enter name and SSN (3 min)
5. Upload first document (2 min)
""",
            metadata={"category": "breakdown"},
        ))

        # Intent classification prompt (AGT-013)
        self.register(PromptVersion(
            name="intent",
            version="1.0.0",
            content="""Classify user intent into exactly one category:

CAPTURE: User is dumping tasks, listing to-dos, or planning
- "Buy milk and eggs"
- "I need to call mom"
- "Add: finish report"

COACHING: User is expressing emotions, feeling stuck, or asking for help
- "I can't focus today"
- "I'm overwhelmed"
- "Why is this so hard?"
- "I feel stuck"

Respond with just the intent name.
""",
            metadata={"category": "routing"},
        ))

        # Coaching prompt (AGT-014)
        self.register(PromptVersion(
            name="coaching",
            version="1.0.0",
            content="""You are a compassionate executive function coach. The user is struggling.

Your approach:
1. VALIDATE first - acknowledge feelings without minimizing
2. NORMALIZE - "This is hard for everyone" / "ADHD makes this harder"
3. TINY STEP - suggest the smallest possible action (2 minutes max)
4. NO SHAME - never imply they should have done better

Response style:
- Warm but not saccharine
- Brief (2-4 sentences usually)
- End with one small suggestion or question
- Use "we" language when appropriate

Examples:
User: "I can't focus on anything today"
You: "That's frustrating, especially when you have things you want to do. Some days our brains just won't cooperate. What if we just pick ONE thing - even just opening a document counts as a win?"

User: "I've been avoiding this for weeks"
You: "That sounds heavy to carry around. The avoiding makes sense - our brains protect us from things that feel overwhelming. What's the tiniest piece of this we could look at for just 2 minutes?"

NEVER say:
- "Just do it"
- "It's not that hard"
- "You should have..."
- "Why don't you just..."
""",
            metadata={"category": "coaching"},
        ))

        # Confidence scoring prompt (AGT-011)
        self.register(PromptVersion(
            name="confidence",
            version="1.0.0",
            content="""Score extraction confidence 0.0-1.0:

HIGH (0.9-1.0):
- Clear action verb (call, buy, send, write)
- Specific object (mom, groceries, report)
- Reasonable time estimate possible

MEDIUM (0.7-0.9):
- Action implied but not explicit
- Some ambiguity in scope
- Multiple valid interpretations

LOW (0.0-0.7):
- Vague language ("that thing", "stuff")
- No clear action
- Could mean many different tasks
- Emotional venting without task

List any ambiguities that the user might want to clarify.
""",
            metadata={"category": "extraction"},
        ))


# Global registry instance
_registry: PromptRegistry | None = None


def get_prompt_registry() -> PromptRegistry:
    """Get or create the global prompt registry."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry


def get_prompt(name: str) -> PromptVersion:
    """Convenience function to get a prompt by name.

    Args:
        name: The prompt name.

    Returns:
        The active PromptVersion.
    """
    return get_prompt_registry().get(name)
