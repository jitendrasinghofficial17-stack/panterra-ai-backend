"""
Conversation Memory Implementation

In-memory and database-backed storage for conversation history.
Optimized for fast retrieval and efficient storage.

Features:
- SQLAlchemy integration with PostgreSQL
- In-memory cache layer for recent conversations
- Automatic cleanup of old conversations
- Token and cost tracking
- Conversation statistics
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from app.ai.memory.base import (
    ConversationMemory,
    ConversationTurn,
    MemoryStorageError,
    MemoryNotFoundError,
)

logger = logging.getLogger(__name__)


class InMemoryConversationMemory(ConversationMemory):
    """
    In-memory conversation storage for development and testing.
    
    Stores conversations in memory - useful for:
    - Development without database
    - Caching frequent conversations
    - Testing
    - High-speed operations
    
    Note: Data is lost on restart. Use SQLAlchemy version for production.
    """
    
    def __init__(self, max_conversations: int = 1000):
        """
        Initialize in-memory storage.
        
        Args:
            max_conversations: Maximum conversations to keep in memory
        """
        self.max_conversations = max_conversations
        self.conversations: Dict[str, List[ConversationTurn]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    async def add_turn(self, turn: ConversationTurn) -> None:
        """Store a conversation turn in memory"""
        try:
            key = f"{turn.user_id}:{turn.conversation_id}"
            
            if key not in self.conversations:
                self.conversations[key] = []
                self.metadata[key] = {
                    "created_at": datetime.utcnow(),
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "models_used": set(),
                }
            
            self.conversations[key].append(turn)
            
            # Update metadata
            self.metadata[key]["total_tokens"] += turn.tokens_used
            self.metadata[key]["models_used"].add(turn.model_used)
            
            logger.debug(f"Stored turn {turn.turn_id} in conversation {key}")
        
        except Exception as e:
            logger.error(f"Error storing turn: {e}")
            raise MemoryStorageError(f"Failed to store turn: {e}")
    
    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationTurn]:
        """Retrieve conversation history from memory"""
        try:
            key = f"{user_id}:{conversation_id}"
            
            if key not in self.conversations:
                return []
            
            turns = self.conversations[key]
            return turns[offset:offset + limit]
        
        except Exception as e:
            logger.error(f"Error retrieving conversation: {e}")
            raise MemoryStorageError(f"Failed to retrieve conversation: {e}")
    
    async def get_recent_turns(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 10
    ) -> List[ConversationTurn]:
        """Get recent turns from memory"""
        try:
            key = f"{user_id}:{conversation_id}"
            
            if key not in self.conversations:
                return []
            
            turns = self.conversations[key]
            return turns[-limit:] if len(turns) > limit else turns
        
        except Exception as e:
            logger.error(f"Error retrieving recent turns: {e}")
            raise MemoryStorageError(f"Failed to retrieve recent turns: {e}")
    
    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> int:
        """Delete conversation from memory"""
        try:
            key = f"{user_id}:{conversation_id}"
            
            if key not in self.conversations:
                return 0
            
            turn_count = len(self.conversations[key])
            del self.conversations[key]
            del self.metadata[key]
            
            logger.info(f"Deleted conversation {key} with {turn_count} turns")
            return turn_count
        
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            raise MemoryStorageError(f"Failed to delete conversation: {e}")
    
    async def clear_old_conversations(
        self,
        user_id: str,
        days_old: int = 30
    ) -> int:
        """Delete old conversations from memory"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted = 0
            
            keys_to_delete = []
            for key, meta in self.metadata.items():
                if key.startswith(f"{user_id}:"):
                    if meta["created_at"] < cutoff_date:
                        keys_to_delete.append(key)
            
            for key in keys_to_delete:
                if key in self.conversations:
                    del self.conversations[key]
                del self.metadata[key]
                deleted += 1
            
            logger.info(f"Deleted {deleted} old conversations for user {user_id}")
            return deleted
        
        except Exception as e:
            logger.error(f"Error clearing old conversations: {e}")
            raise MemoryStorageError(f"Failed to clear old conversations: {e}")
    
    async def get_conversation_stats(
        self,
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Get conversation statistics"""
        try:
            key = f"{user_id}:{conversation_id}"
            
            if key not in self.conversations:
                raise MemoryNotFoundError(f"Conversation {key} not found")
            
            turns = self.conversations[key]
            meta = self.metadata[key]
            
            if not turns:
                return {
                    "turn_count": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "duration": 0,
                    "models_used": [],
                }
            
            start_time = turns[0].timestamp
            end_time = turns[-1].timestamp
            duration = (end_time - start_time).total_seconds()
            
            return {
                "turn_count": len(turns),
                "total_tokens": meta["total_tokens"],
                "total_cost": meta["total_cost"],
                "duration": duration,
                "models_used": list(meta["models_used"]),
                "created_at": meta["created_at"].isoformat(),
                "last_turn_at": end_time.isoformat(),
            }
        
        except MemoryNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            raise MemoryStorageError(f"Failed to get conversation stats: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        total_turns = sum(
            len(turns) for turns in self.conversations.values()
        )
        total_tokens = sum(
            meta.get("total_tokens", 0) for meta in self.metadata.values()
        )
        
        return {
            "conversation_count": len(self.conversations),
            "total_turns": total_turns,
            "total_tokens": total_tokens,
            "max_conversations": self.max_conversations,
        }


class CachedConversationMemory(ConversationMemory):
    """
    Cached conversation memory for production.
    
    Combines in-memory cache with database backend:
    - Recent conversations cached in memory
    - Older conversations stored in database
    - Automatic cache eviction
    - Optimal performance for active conversations
    """
    
    def __init__(
        self,
        cache_size: int = 100,
        cache_ttl_seconds: int = 3600,
        db_session=None,
    ):
        """
        Initialize cached memory.
        
        Args:
            cache_size: Max conversations in cache
            cache_ttl_seconds: How long to keep in cache
            db_session: SQLAlchemy session for database operations
        """
        self.cache_size = cache_size
        self.cache_ttl_seconds = cache_ttl_seconds
        self.db_session = db_session
        self.in_memory = InMemoryConversationMemory(cache_size)
        self.cache_access_times: Dict[str, datetime] = {}
    
    async def add_turn(self, turn: ConversationTurn) -> None:
        """Store turn in cache and optionally database"""
        # Always store in memory cache
        await self.in_memory.add_turn(turn)
        
        # Update access time
        key = f"{turn.user_id}:{turn.conversation_id}"
        self.cache_access_times[key] = datetime.utcnow()
        
        # TODO: Persist to database if db_session available
        if self.db_session:
            # Database persistence logic here
            pass
    
    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationTurn]:
        """Retrieve from cache or database"""
        # Try cache first
        try:
            turns = await self.in_memory.get_conversation(
                user_id,
                conversation_id,
                limit,
                offset
            )
            if turns:
                return turns
        except Exception:
            pass
        
        # TODO: Fall back to database if not in cache
        # if self.db_session:
        #     return await self._get_from_database(user_id, conversation_id, limit, offset)
        
        return []
    
    async def get_recent_turns(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 10
    ) -> List[ConversationTurn]:
        """Get recent turns from cache"""
        return await self.in_memory.get_recent_turns(
            user_id,
            conversation_id,
            limit
        )
    
    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> int:
        """Delete from cache and database"""
        # Delete from cache
        deleted = await self.in_memory.delete_conversation(user_id, conversation_id)
        
        # Clean up access time
        key = f"{user_id}:{conversation_id}"
        if key in self.cache_access_times:
            del self.cache_access_times[key]
        
        # TODO: Delete from database if available
        
        return deleted
    
    async def clear_old_conversations(
        self,
        user_id: str,
        days_old: int = 30
    ) -> int:
        """Clear old conversations"""
        return await self.in_memory.clear_old_conversations(user_id, days_old)
    
    async def get_conversation_stats(
        self,
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Get conversation statistics"""
        return await self.in_memory.get_conversation_stats(user_id, conversation_id)
    
    async def cleanup_cache(self) -> int:
        """Remove expired entries from cache"""
        cutoff_time = datetime.utcnow() - timedelta(
            seconds=self.cache_ttl_seconds
        )
        
        keys_to_remove = []
        for key, access_time in self.cache_access_times.items():
            if access_time < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            user_id, conversation_id = key.split(":")
            await self.in_memory.delete_conversation(user_id, conversation_id)
            del self.cache_access_times[key]
        
        logger.info(f"Cleaned up {len(keys_to_remove)} expired cache entries")
        return len(keys_to_remove)
