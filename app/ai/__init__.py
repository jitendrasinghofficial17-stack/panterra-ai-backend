"""
PANTERRA AI Domain

Provides AI-powered trading intelligence with support for multiple LLM providers,
conversation management, memory systems, and tool orchestration.

Architecture:
- Providers: Abstract interface for OpenAI, Anthropic, Gemini, Local models
- Memory: Short-term conversation history + long-term knowledge base
- Prompts: Centralized template system with engineering utilities
- Conversation: State management and multi-turn dialogue
- Tools: Function calling and service integration
- Orchestration: Multi-agent coordination and reasoning
"""

from app.ai.providers.factory import get_provider, get_default_provider
from app.ai.conversation.manager import ConversationManager
from app.ai.memory.conversation import ConversationMemory

__all__ = [
    "get_provider",
    "get_default_provider",
    "ConversationManager",
    "ConversationMemory",
]
