"""
AI Provider Base Class

Abstract interface for all AI providers (OpenAI, Anthropic, Gemini, Local).
Defines the contract that all provider implementations must follow.

This abstraction allows swapping providers without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class RateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded"""
    pass


class AuthenticationError(ProviderError):
    """Raised when API authentication fails"""
    pass


class ModelNotFoundError(ProviderError):
    """Raised when requested model is not available"""
    pass


class TimeoutError(ProviderError):
    """Raised when provider request times out"""
    pass


@dataclass
class CompletionRequest:
    """Request parameters for text completion"""
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    top_k: Optional[int] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CompletionResponse:
    """Response from text completion"""
    content: str
    model: str
    provider: str
    tokens_used: int
    input_tokens: int
    output_tokens: int
    finish_reason: str
    raw_response: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ModelInfo:
    """Information about an AI model"""
    model_id: str
    provider: str
    display_name: str
    description: Optional[str] = None
    context_window: int = 4096
    max_output_tokens: int = 2048
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_streaming: bool = True
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    release_date: Optional[str] = None
    capabilities: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}


class AIProvider(ABC):
    """
    Abstract base class for all AI providers.
    
    All provider implementations must inherit from this class and implement
    all abstract methods. This ensures consistent behavior across providers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration dictionary containing:
                - api_key: API authentication key
                - api_url: API endpoint URL
                - timeout_seconds: Request timeout
                - max_retries: Maximum retry attempts
                - retry_delay_seconds: Delay between retries
                - enable_streaming: Whether to support streaming
        """
        self.config = config
        self.api_key = config.get("api_key")
        self.api_url = config.get("api_url")
        self.timeout_seconds = config.get("timeout_seconds", 60)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay_seconds = config.get("retry_delay_seconds", 1.0)
        self.enable_streaming = config.get("enable_streaming", True)
        
        # Validate configuration
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate provider configuration.
        
        Raises:
            AuthenticationError: If configuration is invalid or incomplete
        """
        pass
    
    @abstractmethod
    async def complete(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """
        Generate a text completion.
        
        Args:
            request: Completion request with prompt and parameters
            
        Returns:
            CompletionResponse with generated text and metadata
            
        Raises:
            AuthenticationError: If API authentication fails
            RateLimitError: If rate limit is exceeded
            ModelNotFoundError: If model doesn't exist
            TimeoutError: If request times out
            ProviderError: For other provider-specific errors
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        """
        Generate a text completion with streaming.
        
        Args:
            request: Completion request
            
        Yields:
            Text chunks as they're generated
            
        Raises:
            ProviderError: For any errors during streaming
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model_id: str) -> ModelInfo:
        """
        Get information about a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            ModelInfo with model details
            
        Raises:
            ModelNotFoundError: If model doesn't exist
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """
        Get list of available models for this provider.
        
        Returns:
            List of ModelInfo for available models
        """
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """
        Validate that the API key is valid and has access.
        
        Returns:
            True if API key is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_id: str
    ) -> float:
        """
        Calculate cost of a completion.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_id: Model used for completion
            
        Returns:
            Cost in USD
        """
        pass
    
    # Telemetry and monitoring methods
    
    def log_completion_tokens(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> None:
        """
        Log token usage for monitoring.
        
        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
        """
        # Override in subclasses for actual logging
        pass
    
    def log_request_latency(
        self,
        model: str,
        latency_ms: float
    ) -> None:
        """
        Log request latency for performance monitoring.
        
        Args:
            model: Model name
            latency_ms: Request latency in milliseconds
        """
        # Override in subclasses for actual logging
        pass
    
    def log_error(
        self,
        model: str,
        error_type: str,
        error_message: str
    ) -> None:
        """
        Log errors for debugging and monitoring.
        
        Args:
            model: Model name
            error_type: Type of error
            error_message: Error description
        """
        # Override in subclasses for actual logging
        pass
    
    # Helper methods
    
    def _format_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Format prompt into messages list.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            List of message dicts for API
        """
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })
        return messages
    
    def _extract_text_from_response(
        self,
        response: Any
    ) -> str:
        """
        Extract text content from provider's response object.
        
        Must be implemented by subclasses based on provider's response format.
        
        Args:
            response: Raw response from provider API
            
        Returns:
            Extracted text content
        """
        raise NotImplementedError("Subclasses must implement _extract_text_from_response")
    
    def _extract_tokens_from_response(
        self,
        response: Any
    ) -> tuple[int, int]:
        """
        Extract token counts from provider's response.
        
        Must be implemented by subclasses.
        
        Args:
            response: Raw response from provider API
            
        Returns:
            Tuple of (input_tokens, output_tokens)
        """
        raise NotImplementedError("Subclasses must implement _extract_tokens_from_response")
