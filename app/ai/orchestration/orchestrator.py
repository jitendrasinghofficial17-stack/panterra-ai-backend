"""
AI Orchestrator

Main orchestration layer coordinating all AI system components.

Coordinates:
- Provider selection and fallback
- Request/response pipelines
- Memory management
- Error handling and recovery
- Streaming responses
- Rate limiting and quotas

This is the primary interface for the rest of the application.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncGenerator
from uuid import uuid4

from app.ai.providers import (
    get_provider,
    get_available_providers,
    switch_provider,
    AIProviderEnum,
    CompletionRequest,
    ProviderError,
)
from app.ai.orchestration.request_pipeline import (
    RequestPipeline,
    RequestValidationError,
)
from app.ai.orchestration.response_pipeline import (
    ResponsePipeline,
    ResponseValidationError,
)
from app.ai.memory.base import MemoryManager

logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Base exception for orchestrator errors"""
    pass


class AIOrchestrator:
    """
    Main AI orchestration engine.
    
    Coordinates all components:
    1. Request Pipeline: Validates and prepares requests
    2. Provider Selection: Chooses best provider based on availability
    3. Provider Execution: Handles retries and fallbacks
    4. Response Pipeline: Processes and validates responses
    5. Memory Persistence: Stores conversations and knowledge
    
    Usage:
        ```python
        orchestrator = AIOrchestrator(memory_manager)
        
        # Single completion
        response = await orchestrator.complete(
            user_message="Hello!",
            user_id="user_123",
            conversation_id="conv_456"
        )
        
        # Streaming completion
        async for chunk in orchestrator.stream(
            user_message="Tell me a story",
            user_id="user_123",
            conversation_id="conv_456"
        ):
            print(chunk, end="")
        ```
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        cost_tracker=None,
        rate_limiter=None,
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
    ):
        """
        Initialize orchestrator.
        
        Args:
            memory_manager: Memory system for persistence
            cost_tracker: Cost tracking system
            rate_limiter: Rate limiting system
            max_retries: Max retry attempts for provider failures
            retry_delay_seconds: Base delay between retries
        """
        self.memory_manager = memory_manager
        self.cost_tracker = cost_tracker
        self.rate_limiter = rate_limiter
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        
        # Initialize pipelines
        self.request_pipeline = RequestPipeline(
            memory_manager=memory_manager,
            rate_limiter=rate_limiter,
        )
        
        self.response_pipeline = ResponsePipeline(
            memory_manager=memory_manager,
            cost_tracker=cost_tracker,
        )
    
    async def complete(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
        model: Optional[str] = None,
        provider: Optional[AIProviderEnum] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion and return full response.
        
        Args:
            user_message: User's input message
            user_id: User identifier
            conversation_id: Conversation identifier
            model: Model to use (uses default if None)
            provider: Provider to use (uses default if None)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Formatted response dict with:
            - content: AI response text
            - tokens: Token usage (input, output, total)
            - model: Model used
            - provider: Provider used
            - latency_ms: Request latency
            - finish_reason: Completion reason
            - metadata: Additional info
            
        Raises:
            OrchestratorError: If completion fails after retries
            RequestValidationError: If request validation fails
        """
        request_start_time = time.time()
        
        try:
            # Stage 1: Process request
            logger.info(
                f"Processing completion for user {user_id} "
                f"in conversation {conversation_id}"
            )
            
            completion_request = await self.request_pipeline.process(
                user_message=user_message,
                user_id=user_id,
                conversation_id=conversation_id,
                model=model,
                provider=provider,
                **kwargs
            )
            
            # Stage 2: Get provider and execute
            provider_instance = get_provider(provider)
            
            response = await self._execute_with_retry(
                provider_instance=provider_instance,
                request=completion_request,
                user_id=user_id,
                provider=provider,
            )
            
            # Stage 3: Process response
            formatted_response = await self.response_pipeline.process(
                response=response,
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=user_message,
                model=completion_request.model,
                provider_name=provider_instance.__class__.__name__,
                request_start_time=request_start_time,
            )
            
            return formatted_response
        
        except RequestValidationError as e:
            logger.error(f"Request validation failed: {e}")
            raise OrchestratorError(f"Invalid request: {e}")
        
        except Exception as e:
            logger.error(f"Completion failed: {e}")
            raise OrchestratorError(f"Completion failed: {e}")
    
    async def stream(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
        model: Optional[str] = None,
        provider: Optional[AIProviderEnum] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming completion.
        
        Yields text chunks as they're generated by the provider.
        
        Args:
            user_message: User's input message
            user_id: User identifier
            conversation_id: Conversation identifier
            model: Model to use
            provider: Provider to use
            **kwargs: Additional parameters
            
        Yields:
            Text chunks as strings
            
        Raises:
            OrchestratorError: If streaming fails
        """
        try:
            # Process request
            completion_request = await self.request_pipeline.process(
                user_message=user_message,
                user_id=user_id,
                conversation_id=conversation_id,
                model=model,
                provider=provider,
                **kwargs
            )
            
            # Get provider
            provider_instance = get_provider(provider)
            
            # Stream response
            full_response = []
            async for chunk in provider_instance.stream(completion_request):
                full_response.append(chunk)
                yield chunk
            
            # Store complete response in memory
            if self.memory_manager:
                try:
                    full_text = "".join(full_response)
                    # Create a stored turn with complete response
                    logger.debug(
                        f"Streaming complete: {len(full_response)} chunks"
                    )
                except Exception as e:
                    logger.warning(f"Error storing streamed response: {e}")
        
        except RequestValidationError as e:
            logger.error(f"Stream request validation failed: {e}")
            raise OrchestratorError(f"Invalid stream request: {e}")
        
        except Exception as e:
            logger.error(f"Stream failed: {e}")
            raise OrchestratorError(f"Stream failed: {e}")
    
    async def _execute_with_retry(
        self,
        provider_instance,
        request: CompletionRequest,
        user_id: str,
        provider: Optional[AIProviderEnum] = None,
    ):
        """
        Execute provider request with retry and fallback logic.
        
        Handles:
        - Retry on transient errors
        - Provider fallback on persistent errors
        - Error logging and tracking
        """
        last_error = None
        attempted_providers = set()
        
        # Prepare list of providers to try
        providers_to_try = [provider_instance]
        if provider:
            attempted_providers.add(provider)
        
        # Add fallback providers
        for alt_provider in get_available_providers().values():
            if alt_provider not in providers_to_try:
                providers_to_try.append(alt_provider)
        
        # Try each provider with retries
        for provider_attempt, prov in enumerate(providers_to_try):
            for retry_attempt in range(self.max_retries):
                try:
                    logger.debug(
                        f"Executing request with {prov.__class__.__name__} "
                        f"(attempt {retry_attempt + 1}/{self.max_retries})"
                    )
                    
                    response = await prov.complete(request)
                    
                    logger.info(
                        f"Completion successful with {prov.__class__.__name__}"
                    )
                    
                    return response
                
                except ProviderError as e:
                    last_error = e
                    
                    # Check if should retry with same provider
                    should_retry = await self.response_pipeline.handle_error(
                        error=e,
                        user_id=user_id,
                        conversation_id="",
                        attempt=retry_attempt + 1,
                        max_attempts=self.max_retries,
                    )
                    
                    if should_retry is None:
                        # Retry signal - wait and continue loop
                        if retry_attempt < self.max_retries - 1:
                            wait_time = self.retry_delay_seconds * (2 ** retry_attempt)
                            logger.info(f"Retrying after {wait_time}s delay")
                            await asyncio.sleep(wait_time)
                            continue
                    else:
                        # Error response - break to try next provider
                        break
                
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    last_error = e
                    break
        
        # All providers exhausted
        if last_error:
            raise OrchestratorError(
                f"All providers failed. Last error: {last_error}"
            )
        else:
            raise OrchestratorError("No available providers")
    
    async def validate_providers(self) -> Dict[AIProviderEnum, bool]:
        """
        Validate all configured providers.
        
        Returns:
            Dictionary mapping provider to validation status
        """
        logger.info("Validating all providers...")
        results = {}
        
        for provider_enum, provider in get_available_providers().items():
            try:
                is_valid = await provider.validate_api_key()
                results[provider_enum] = is_valid
                status = "✓" if is_valid else "✗"
                logger.info(f"{status} {provider_enum.value}")
            except Exception as e:
                logger.error(f"✗ {provider_enum.value}: {e}")
                results[provider_enum] = False
        
        return results
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dictionary with:
            - orchestrator: Orchestrator status
            - providers: Provider availability
            - memory: Memory system status
            - last_update: Timestamp
        """
        providers_status = await self.validate_providers()
        
        return {
            "status": "operational",
            "orchestrator": {
                "max_retries": self.max_retries,
                "retry_delay_seconds": self.retry_delay_seconds,
            },
            "providers": {
                provider.value: is_valid
                for provider, is_valid in providers_status.items()
            },
            "memory": {
                "enabled": self.memory_manager is not None,
            },
            "timestamp": time.time(),
        }


# Convenience function for creating orchestrator with defaults
def create_orchestrator(
    memory_manager: Optional[MemoryManager] = None,
    **kwargs
) -> AIOrchestrator:
    """
    Create AI orchestrator with default configuration.
    
    Args:
        memory_manager: Memory system (optional)
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured AIOrchestrator instance
    """
    return AIOrchestrator(
        memory_manager=memory_manager,
        **kwargs
    )
