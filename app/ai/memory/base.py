"""
Memory System Base Classes

Abstract interfaces for memory storage and retrieval.
Supports short-term (conversation) and long-term (knowledge) memory.

Architecture:
- ConversationMemory: Short-term turn-by-turn history
- KnowledgeMemory: Long-term embeddings and semantic search
- MemoryManager: Unified interface for memory operations
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemoryItem:
    """Single memory item"""
    key: str
    value: Any
    timestamp: datetime
    ttl_seconds: Optional[int] = None
    importance_score: float = 0.5
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_expired(self) -> bool:
        """Check if memory item has expired"""
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.utcnow() - self.timestamp).total_seconds()
        return elapsed > self.ttl_seconds


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""
    turn_id: str
    user_id: str
    conversation_id: str
    user_message: str
    ai_response: str
    timestamp: datetime
    tokens_used: int
    model_used: str
    provider_used: str
    finish_reason: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResult:
    """Result from memory search"""
    item: MemoryItem
    similarity_score: float
    rank: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryError(Exception):
    """Base exception for memory system errors"""
    pass


class MemoryNotFoundError(MemoryError):
    """Raised when memory item not found"""
    pass


class MemoryStorageError(MemoryError):
    """Raised when storage operation fails"""
    pass


class ConversationMemory(ABC):
    """
    Abstract base class for conversation memory storage.
    
    Stores short-term conversation history with:
    - Turn-by-turn exchanges
    - Token tracking
    - Cost tracking
    - Metadata (model, provider, timestamps)
    """
    
    @abstractmethod
    async def add_turn(
        self,
        turn: ConversationTurn
    ) -> None:
        """
        Store a conversation turn.
        
        Args:
            turn: ConversationTurn object
            
        Raises:
            MemoryStorageError: If storage fails
        """
        pass
    
    @abstractmethod
    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationTurn]:
        """
        Retrieve conversation history.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            limit: Max turns to retrieve
            offset: Pagination offset
            
        Returns:
            List of ConversationTurn ordered by timestamp
            
        Raises:
            MemoryStorageError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_recent_turns(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 10
    ) -> List[ConversationTurn]:
        """
        Get recent turns from conversation.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            limit: Number of recent turns to retrieve
            
        Returns:
            List of recent ConversationTurn
        """
        pass
    
    @abstractmethod
    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> int:
        """
        Delete entire conversation.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            
        Returns:
            Number of turns deleted
        """
        pass
    
    @abstractmethod
    async def clear_old_conversations(
        self,
        user_id: str,
        days_old: int = 30
    ) -> int:
        """
        Delete conversations older than specified days.
        
        Args:
            user_id: User identifier
            days_old: Delete conversations older than this many days
            
        Returns:
            Number of conversations deleted
        """
        pass
    
    @abstractmethod
    async def get_conversation_stats(
        self,
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics for a conversation.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            
        Returns:
            Dictionary with stats:
            - turn_count: Number of turns
            - total_tokens: Total tokens used
            - total_cost: Total cost in USD
            - duration: Conversation duration
            - models_used: List of models used
        """
        pass


class KnowledgeMemory(ABC):
    """
    Abstract base class for knowledge memory (long-term).
    
    Stores and retrieves information using:
    - Vector embeddings for semantic search
    - Metadata filtering
    - Relevance scoring
    - Document chunking
    """
    
    @abstractmethod
    async def index_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Index a document for semantic search.
        
        Args:
            document_id: Unique document identifier
            content: Document text content
            metadata: Optional metadata (author, source, etc.)
            
        Raises:
            MemoryStorageError: If indexing fails
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search knowledge base using semantic similarity.
        
        Args:
            query: Search query
            limit: Max results to return
            score_threshold: Min similarity score (0.0-1.0)
            filters: Metadata filters to apply
            
        Returns:
            List of SearchResult ordered by relevance
            
        Raises:
            MemoryStorageError: If search fails
        """
        pass
    
    @abstractmethod
    async def delete_document(
        self,
        document_id: str
    ) -> bool:
        """
        Delete a document from knowledge base.
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def reindex_all(self) -> int:
        """
        Rebuild all indexes.
        
        Useful after major changes or corruption.
        
        Returns:
            Number of documents reindexed
        """
        pass
    
    @abstractmethod
    async def get_document_count(self) -> int:
        """
        Get total number of documents in knowledge base.
        
        Returns:
            Document count
        """
        pass


class MemoryManager(ABC):
    """
    Unified interface for all memory operations.
    
    Coordinates conversation memory and knowledge memory.
    Handles memory lifecycle, cleanup, and optimization.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize memory systems and create indexes"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Clean shutdown of memory systems"""
        pass
    
    @abstractmethod
    async def add_conversation_turn(
        self,
        turn: ConversationTurn
    ) -> None:
        """Store conversation turn"""
        pass
    
    @abstractmethod
    async def get_conversation_context(
        self,
        user_id: str,
        conversation_id: str,
        context_size: int = 10
    ) -> str:
        """
        Get formatted conversation context for LLM.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            context_size: Number of turns to include
            
        Returns:
            Formatted context string for system prompt
        """
        pass
    
    @abstractmethod
    async def search_knowledge(
        self,
        query: str,
        limit: int = 5
    ) -> List[SearchResult]:
        """Search knowledge base"""
        pass
    
    @abstractmethod
    async def add_knowledge(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add content to knowledge base"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> Dict[str, int]:
        """
        Clean up expired and old data.
        
        Returns:
            Dictionary with cleanup stats:
            - conversations_deleted: Count of deleted conversations
            - memories_expired: Count of expired memories
            - total_freed_bytes: Approximate space freed
        """
        pass
