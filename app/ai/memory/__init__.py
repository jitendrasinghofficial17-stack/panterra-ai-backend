"""
AI Memory Package

Memory system for conversation history and knowledge base.

Exports:
- ConversationMemory: Base class for conversation storage
- KnowledgeMemory: Base class for knowledge storage
- MemoryManager: Unified memory interface
- InMemoryConversationMemory: In-memory implementation
- CachedConversationMemory: Cached with database backend

Usage:
    from app.ai.memory import InMemoryConversationMemory, ConversationTurn
    
    # Create memory storage
    memory = InMemoryConversationMemory()
    
    # Store conversation turn
    turn = ConversationTurn(
        turn_id="turn_123",
        user_id="user_456",
        conversation_id="conv_789",
        user_message="Hello!",
        ai_response="Hi there!",
        timestamp=datetime.utcnow(),
        tokens_used=50,
        model_used="gpt-4",
        provider_used="openai",
        finish_reason="stop"
    )
    await memory.add_turn(turn)
    
    # Retrieve conversation
    turns = await memory.get_conversation("user_456", "conv_789")
"""

from app.ai.memory.base import (
    ConversationMemory,
    KnowledgeMemory,
    MemoryManager,
    ConversationTurn,
    MemoryItem,
    SearchResult,
    MemoryError,
    MemoryNotFoundError,
    MemoryStorageError,
)

from app.ai.memory.conversation import (
    InMemoryConversationMemory,
    CachedConversationMemory,
)

__all__ = [
    # Base classes
    "ConversationMemory",
    "KnowledgeMemory",
    "MemoryManager",
    
    # Data classes
    "ConversationTurn",
    "MemoryItem",
    "SearchResult",
    
    # Errors
    "MemoryError",
    "MemoryNotFoundError",
    "MemoryStorageError",
    
    # Implementations
    "InMemoryConversationMemory",
    "CachedConversationMemory",
]
