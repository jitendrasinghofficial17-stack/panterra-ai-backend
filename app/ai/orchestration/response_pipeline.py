"""
AI Response Pipeline

Processes and validates responses from AI providers.
Handles:
- Response validation and parsing
- Error recovery and fallback strategies
- Token and cost tracking
- Memory persistence
- Response formatting for clients
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time

from app.ai.providers import (
    CompletionResponse,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    TimeoutError as ProviderTimeoutError,
)
from app.ai.memory.base import (
    MemoryManager,
    ConversationTurn,
    MemoryError,
)

logger = logging.getLogger(__name__)


class ResponseValidationError(Exception):
    """Raised when response validation fails"""
    pass


class ResponseProcessingError(Exception):
    """Raised when response processing fails"""
    pass


class ResponsePipeline:
    """
    Pipeline for processing responses from AI providers.
    
    Stages:
    1. Validation - Verify response format and completeness
    2. Error Handling - Detect and handle provider errors
    3. Parsing - Extract content and metadata
    4. Tracking - Log tokens and costs
    5. Persistence - Store in memory/database
    6. Formatting - Format for client consumption
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        cost_tracker=None,
        error_handler=None,
    ):
        """
        Initialize response pipeline.
        
        Args:
            memory_manager: Memory system for persistence
            cost_tracker: Cost tracking implementation
            error_handler: Error handling and recovery logic
        """
        self.memory_manager = memory_manager
        self.cost_tracker = cost_tracker
        self.error_handler = error_handler
    
    async def process(
        self,
        response: CompletionResponse,
        user_id: str,
        conversation_id: str,
        user_message: str,
        model: str,
        provider_name: str,
        request_start_time: float,
    ) -> Dict[str, Any]:
        """
        Process provider response through all pipeline stages.
        
        Args:
            response: Provider's CompletionResponse
            user_id: User identifier
            conversation_id: Conversation identifier
            user_message: Original user message
            model: Model used
            provider_name: Provider name
            request_start_time: Request start timestamp (for latency)
            
        Returns:
            Formatted response dict for client
            
        Raises:
            ResponseValidationError: If validation fails
            ResponseProcessingError: If processing fails
        """
        # Stage 1: Validate
        self._validate_response(response)
        
        # Stage 2: Parse
        parsed_content = self._parse_response(response)
        
        # Stage 3: Track tokens and costs
        latency_ms = (time.time() - request_start_time) * 1000
        await self._track_usage(
            user_id,
            response,
            latency_ms,
            model,
        )
        
        # Stage 4: Persist to memory
        if self.memory_manager:
            await self._persist_to_memory(
                user_id,
                conversation_id,
                user_message,
                parsed_content,
                response,
                model,
                provider_name,
            )
        
        # Stage 5: Format for client
        formatted_response = self._format_response(
            parsed_content,
            response,
            latency_ms,
        )
        
        logger.info(
            f"Processed response for user {user_id} "
            f"({response.tokens_used} tokens, {latency_ms:.0f}ms)"
        )
        
        return formatted_response
    
    def _validate_response(self, response: CompletionResponse) -> None:
        """
        Validate response format and completeness.
        
        Raises:
            ResponseValidationError: If validation fails
        """
        if not response:
            raise ResponseValidationError("Response is None")
        
        if not isinstance(response, CompletionResponse):
            raise ResponseValidationError(
                f"Response must be CompletionResponse, "
                f"got {type(response)}"
            )
        
        if not response.content:
            raise ResponseValidationError("Response content is empty")
        
        if response.tokens_used <= 0:
            raise ResponseValidationError(
                "Invalid token count in response"
            )
        
        if not response.model:
            raise ResponseValidationError("Response model not specified")
        
        if not response.provider:
            raise ResponseValidationError("Response provider not specified")
        
        logger.debug("Response validation passed")
    
    def _parse_response(self, response: CompletionResponse) -> str:
        """
        Extract and clean response content.
        
        Handles:
        - Whitespace normalization
        - Invalid character removal
        - Length validation
        """
        content = response.content.strip()
        
        # Remove null bytes and control characters
        content = "".join(
            char for char in content
            if ord(char) >= 32 or char in "\n\t\r"
        )
        
        # Normalize whitespace
        content = "\n".join(
            line.rstrip() for line in content.split("\n")
        )
        
        if not content:
            raise ResponseProcessingError("No valid content in response")
        
        return content
    
    async def _track_usage(
        self,
        user_id: str,
        response: CompletionResponse,
        latency_ms: float,
        model: str,
    ) -> None:
        """
        Track token usage and costs.
        
        Logs to cost tracker and monitoring systems.
        """
        try:
            # Track with cost tracker if available
            if self.cost_tracker:
                cost = self.cost_tracker.calculate_cost(
                    response.input_tokens,
                    response.output_tokens,
                    model,
                )
                await self.cost_tracker.track_usage(
                    user_id=user_id,
                    model=model,
                    provider=response.provider,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost=cost,
                    latency_ms=latency_ms,
                )
            
            # Log metrics
            logger.info(
                f"User {user_id} | Model: {model} | "
                f"Tokens: {response.tokens_used} | "
                f"Latency: {latency_ms:.0f}ms"
            )
        
        except Exception as e:
            logger.warning(f"Error tracking usage: {e}")
    
    async def _persist_to_memory(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        completion_response: CompletionResponse,
        model: str,
        provider: str,
    ) -> None:
        """
        Store conversation turn in memory system.
        
        Handles memory errors gracefully to not block response.
        """
        if not self.memory_manager:
            return
        
        try:
            turn = ConversationTurn(
                turn_id=f"{user_id}:{conversation_id}:{int(time.time() * 1000)}",
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=user_message,
                ai_response=ai_response,
                timestamp=datetime.utcnow(),
                tokens_used=completion_response.tokens_used,
                model_used=model,
                provider_used=provider,
                finish_reason=completion_response.finish_reason,
                metadata={
                    "input_tokens": completion_response.input_tokens,
                    "output_tokens": completion_response.output_tokens,
                },
            )
            
            await self.memory_manager.add_conversation_turn(turn)
            logger.debug(f"Stored conversation turn {turn.turn_id}")
        
        except MemoryError as e:
            logger.warning(f"Error persisting to memory: {e}")
        except Exception as e:
            logger.error(f"Unexpected error persisting to memory: {e}")
    
    def _format_response(
        self,
        content: str,
        response: CompletionResponse,
        latency_ms: float,
    ) -> Dict[str, Any]:
        """
        Format response for client consumption.
        
        Returns:
            Dictionary with:
            - content: AI response text
            - model: Model used
            - provider: Provider used
            - tokens_used: Total tokens
            - finish_reason: Completion reason
            - latency_ms: Request latency
            - timestamp: Response timestamp
            - metadata: Additional metadata
        """
        return {
            "content": content,
            "model": response.model,
            "provider": response.provider,
            "tokens": {
                "input": response.input_tokens,
                "output": response.output_tokens,
                "total": response.tokens_used,
            },
            "finish_reason": response.finish_reason,
            "latency_ms": round(latency_ms, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": response.metadata or {},
        }
    
    async def handle_error(
        self,
        error: Exception,
        user_id: str,
        conversation_id: str,
        attempt: int,
        max_attempts: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Handle provider errors with recovery strategies.
        
        Strategies:
        - RateLimitError: Retry with exponential backoff
        - AuthenticationError: Fail immediately
        - ModelNotFoundError: Suggest alternative model
        - TimeoutError: Retry or use fallback provider
        - Generic errors: Log and return error to user
        
        Args:
            error: Exception from provider
            user_id: User identifier
            conversation_id: Conversation identifier
            attempt: Current attempt number
            max_attempts: Maximum retry attempts
            
        Returns:
            Error response dict or None if should retry
        """
        error_type = type(error).__name__
        
        logger.error(
            f"Provider error for user {user_id}: "
            f"{error_type} - {str(error)}"
        )
        
        # Rate limit errors - can retry
        if isinstance(error, RateLimitError):
            if attempt < max_attempts:
                logger.info(
                    f"Rate limited, attempt {attempt}/{max_attempts}. "
                    f"Retrying..."
                )
                return None  # Signal to retry
            return self._format_error_response(
                "Too many requests. Please try again later.",
                "rate_limit_exceeded",
                429,
            )
        
        # Authentication errors - fail immediately
        if isinstance(error, AuthenticationError):
            logger.error("Authentication failed with provider")
            return self._format_error_response(
                "Authentication error. Please check API configuration.",
                "authentication_error",
                401,
            )
        
        # Model not found - suggest alternatives
        if isinstance(error, ModelNotFoundError):
            logger.error(f"Model not found: {error}")
            return self._format_error_response(
                f"Model not available. {str(error)}",
                "model_not_found",
                404,
            )
        
        # Timeout errors - can retry
        if isinstance(error, ProviderTimeoutError):
            if attempt < max_attempts:
                logger.info(
                    f"Request timeout, attempt {attempt}/{max_attempts}. "
                    f"Retrying..."
                )
                return None  # Signal to retry
            return self._format_error_response(
                "Request timed out. Please try again.",
                "timeout",
                504,
            )
        
        # Generic provider errors
        if isinstance(error, ProviderError):
            return self._format_error_response(
                "Provider error occurred. Please try again.",
                "provider_error",
                503,
            )
        
        # Unknown errors
        logger.error(f"Unknown error type: {error_type}")
        return self._format_error_response(
            "An unexpected error occurred. Please try again.",
            "internal_error",
            500,
        )
    
    def _format_error_response(
        self,
        message: str,
        error_type: str,
        status_code: int,
    ) -> Dict[str, Any]:
        """Format error response for client"""
        return {
            "error": True,
            "message": message,
            "error_type": error_type,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
        }
