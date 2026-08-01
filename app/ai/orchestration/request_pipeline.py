"""
AI Request Pipeline

Processes and validates incoming requests before sending to providers.
Handles:
- Input validation and sanitization
- Context building from memory
- Token estimation
- Request formatting for different providers
- Rate limiting and quota checks
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib

from app.ai.providers import (
    CompletionRequest,
    AIProviderEnum,
    get_ai_config,
)
from app.ai.memory.base import MemoryManager

logger = logging.getLogger(__name__)


class RequestValidationError(Exception):
    """Raised when request validation fails"""
    pass


class RequestPipeline:
    """
    Pipeline for processing incoming AI requests.
    
    Stages:
    1. Validation - Check request format and parameters
    2. Sanitization - Clean and normalize input
    3. Context Loading - Retrieve conversation history and knowledge
    4. Formatting - Convert to provider-specific format
    5. Rate Limiting - Check quotas and rate limits
    6. Estimation - Estimate tokens and costs
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        rate_limiter=None,
    ):
        """
        Initialize request pipeline.
        
        Args:
            memory_manager: Memory system for context
            rate_limiter: Rate limiting implementation
        """
        self.memory_manager = memory_manager
        self.rate_limiter = rate_limiter
        self.config = get_ai_config()
    
    async def process(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
        model: Optional[str] = None,
        provider: Optional[AIProviderEnum] = None,
        **kwargs
    ) -> CompletionRequest:
        """
        Process incoming request through all pipeline stages.
        
        Args:
            user_message: User's input message
            user_id: User identifier
            conversation_id: Conversation identifier
            model: Model to use (uses default if None)
            provider: Provider to use (uses default if None)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Processed CompletionRequest ready for provider
            
        Raises:
            RequestValidationError: If validation fails
        """
        # Stage 1: Validate
        self._validate_request(user_message, user_id, conversation_id)
        
        # Stage 2: Sanitize
        sanitized_message = self._sanitize_input(user_message)
        
        # Stage 3: Build context
        context = await self._build_context(
            user_id,
            conversation_id,
            sanitized_message
        )
        
        # Stage 4: Check rate limits
        if self.rate_limiter:
            await self._check_rate_limits(user_id)
        
        # Stage 5: Format request
        request = self._format_request(
            user_message=sanitized_message,
            context=context,
            model=model,
            provider=provider,
            **kwargs
        )
        
        logger.info(
            f"Processed request for user {user_id} "
            f"in conversation {conversation_id}"
        )
        
        return request
    
    def _validate_request(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
    ) -> None:
        """Validate request format and parameters"""
        if not user_message or not isinstance(user_message, str):
            raise RequestValidationError("user_message must be non-empty string")
        
        if not user_id or not isinstance(user_id, str):
            raise RequestValidationError("user_id must be non-empty string")
        
        if not conversation_id or not isinstance(conversation_id, str):
            raise RequestValidationError(
                "conversation_id must be non-empty string"
            )
        
        if len(user_message) > 100000:
            raise RequestValidationError(
                "Message exceeds maximum length of 100,000 characters"
            )
        
        logger.debug("Request validation passed")
    
    def _sanitize_input(self, user_message: str) -> str:
        """
        Sanitize and normalize user input.
        
        - Remove control characters
        - Normalize whitespace
        - Trim to reasonable length
        """
        # Remove null bytes and control characters
        sanitized = "".join(
            char for char in user_message
            if ord(char) >= 32 or char in "\n\t\r"
        )
        
        # Normalize whitespace
        sanitized = " ".join(sanitized.split())
        
        # Trim trailing/leading whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    async def _build_context(
        self,
        user_id: str,
        conversation_id: str,
        current_message: str,
    ) -> str:
        """
        Build conversation context from memory.
        
        Retrieves recent conversation history and relevant knowledge
        to provide as context to the AI model.
        """
        context_parts = []
        
        # Add conversation history
        if self.memory_manager and self.config.enable_conversation_history:
            try:
                conversation_context = (
                    await self.memory_manager.get_conversation_context(
                        user_id,
                        conversation_id,
                        context_size=self.config.conversation_history_limit,
                    )
                )
                if conversation_context:
                    context_parts.append(
                        f"Previous conversation:\n{conversation_context}"
                    )
            except Exception as e:
                logger.warning(f"Error loading conversation context: {e}")
        
        # Add relevant knowledge
        if self.memory_manager and self.config.enable_memory_system:
            try:
                search_results = (
                    await self.memory_manager.search_knowledge(
                        current_message,
                        limit=5,
                    )
                )
                if search_results:
                    knowledge_context = "\n".join(
                        f"- {result.item.value}"
                        for result in search_results
                    )
                    context_parts.append(
                        f"Relevant knowledge:\n{knowledge_context}"
                    )
            except Exception as e:
                logger.warning(f"Error loading knowledge context: {e}")
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    async def _check_rate_limits(self, user_id: str) -> None:
        """Check rate limiting quotas"""
        if not self.rate_limiter:
            return
        
        try:
            is_allowed = await self.rate_limiter.check_limit(user_id)
            if not is_allowed:
                raise RequestValidationError(
                    "Rate limit exceeded. Please try again later."
                )
        except RequestValidationError:
            raise
        except Exception as e:
            logger.warning(f"Error checking rate limits: {e}")
    
    def _format_request(
        self,
        user_message: str,
        context: str,
        model: Optional[str] = None,
        provider: Optional[AIProviderEnum] = None,
        **kwargs
    ) -> CompletionRequest:
        """
        Format validated request into CompletionRequest.
        
        Applies configuration defaults and builds final request object.
        """
        # Use defaults if not specified
        if model is None:
            model = self.config.default_model.value
        
        if provider is None:
            provider = self.config.default_provider
        
        # Build system prompt
        system_prompt = self._build_system_prompt(context, kwargs)
        
        # Extract model-specific parameters
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        top_p = kwargs.get("top_p", 1.0)
        top_k = kwargs.get("top_k", None)
        
        # Create request
        request = CompletionRequest(
            prompt=user_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            system_prompt=system_prompt,
            metadata={
                "provider": provider.value,
                "formatted_at": datetime.utcnow().isoformat(),
            }
        )
        
        return request
    
    def _build_system_prompt(
        self,
        context: str,
        kwargs: Dict[str, Any],
    ) -> str:
        """Build system prompt from configuration and context"""
        system_prompt = kwargs.get(
            "system_prompt",
            "You are a helpful AI assistant."
        )
        
        if context:
            system_prompt = f"{system_prompt}\n\nContext:\n{context}"
        
        return system_prompt
    
    def estimate_tokens(self, text: str, model: str) -> int:
        """
        Estimate token count for text.
        
        Uses approximate calculation based on character count.
        For precise counting, use provider-specific tokenizers.
        """
        # Rough estimate: ~4 characters per token
        # This varies by model and tokenizer
        estimated = len(text) // 4
        return max(1, estimated)  # At least 1 token
