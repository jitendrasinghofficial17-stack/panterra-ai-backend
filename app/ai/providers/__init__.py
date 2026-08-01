"""
AI Providers Package

Public API for AI provider system.
Exports factory functions and base classes for easy access.

Usage:
    from app.ai.providers import get_provider, AIProviderEnum
    
    # Get default provider
    provider = get_provider()
    
    # Get specific provider
    provider = get_provider(AIProviderEnum.OPENAI)
    
    # Use provider
    response = await provider.complete(request)
"""

from app.ai.providers.base import (
    AIProvider,
    CompletionRequest,
    CompletionResponse,
    ModelInfo,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    TimeoutError,
)

from app.ai.providers.factory import (
    ProviderFactory,
    ProviderNotConfiguredError,
    get_provider,
    get_default_provider,
    get_available_providers,
    switch_provider,
)

from app.ai.config import (
    AIProvider as AIProviderEnum,
    AIModel,
    AIConfig,
    AIConfigManager,
    get_ai_config,
)

__all__ = [
    # Base classes
    "AIProvider",
    "AIProviderEnum",
    
    # Request/Response
    "CompletionRequest",
    "CompletionResponse",
    "ModelInfo",
    
    # Errors
    "ProviderError",
    "RateLimitError",
    "AuthenticationError",
    "ModelNotFoundError",
    "TimeoutError",
    "ProviderNotConfiguredError",
    
    # Factory
    "ProviderFactory",
    "get_provider",
    "get_default_provider",
    "get_available_providers",
    "switch_provider",
    
    # Configuration
    "AIModel",
    "AIConfig",
    "AIConfigManager",
    "get_ai_config",
]
