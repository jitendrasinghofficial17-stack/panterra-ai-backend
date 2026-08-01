"""
AI Provider Factory

Factory pattern for creating and managing AI provider instances.
Handles provider instantiation, discovery, and runtime switching.

This is the main entry point for interacting with AI providers.
Abstracts away provider-specific details from business logic.
"""

import logging
from typing import Optional, Dict, Type, Any
from app.ai.config import (
    AIProvider as AIProviderEnum,
    get_ai_config,
    AIConfigManager,
)
from app.ai.providers.base import AIProvider, ProviderError

logger = logging.getLogger(__name__)


# Import provider implementations
from app.ai.providers.openai import OpenAIProvider


class ProviderNotConfiguredError(ProviderError):
    """Raised when a provider is not configured"""
    pass


class ProviderFactory:
    """
    Factory for creating and managing AI provider instances.
    
    Features:
    - Provider discovery and instantiation
    - Runtime provider switching
    - Provider availability checking
    - Singleton pattern for provider instances
    - Configuration management
    """
    
    # Provider class mapping
    _PROVIDER_CLASSES: Dict[AIProviderEnum, Type[AIProvider]] = {
        AIProviderEnum.OPENAI: OpenAIProvider,
        # AIProviderEnum.ANTHROPIC: AnthropicProvider,  # Coming soon
        # AIProviderEnum.GEMINI: GeminiProvider,        # Coming soon
        # AIProviderEnum.LOCAL: LocalProvider,          # Coming soon
    }
    
    # Singleton instances cache
    _instances: Dict[AIProviderEnum, AIProvider] = {}
    
    # Configuration manager
    _config_manager: AIConfigManager = None
    
    def __init__(self):
        """Initialize provider factory with configuration"""
        if not self._config_manager:
            ProviderFactory._config_manager = AIConfigManager()
    
    @classmethod
    def register_provider(
        cls,
        provider: AIProviderEnum,
        provider_class: Type[AIProvider]
    ) -> None:
        """
        Register a new provider implementation.
        
        Allows runtime registration of custom provider implementations.
        
        Args:
            provider: Provider enum value
            provider_class: Provider class that implements AIProvider
            
        Raises:
            ValueError: If provider_class doesn't inherit from AIProvider
        """
        if not issubclass(provider_class, AIProvider):
            raise ValueError(
                f"{provider_class} must inherit from AIProvider"
            )
        
        cls._PROVIDER_CLASSES[provider] = provider_class
        logger.info(f"Registered provider: {provider.value}")
    
    @classmethod
    def get_provider(
        cls,
        provider: Optional[AIProviderEnum] = None
    ) -> AIProvider:
        """
        Get or create a provider instance.
        
        Implements singleton pattern - same instance returned for same provider.
        Automatically selects default provider if none specified.
        
        Args:
            provider: Provider enum (uses default if None)
            
        Returns:
            Provider instance ready for use
            
        Raises:
            ProviderNotConfiguredError: If provider not configured
            ValueError: If provider not registered
            
        Example:
            ```python
            # Get default provider
            provider = ProviderFactory.get_provider()
            
            # Get specific provider
            provider = ProviderFactory.get_provider(AIProviderEnum.OPENAI)
            
            # Use provider
            response = await provider.complete(request)
            ```
        """
        # Use default if not specified
        if provider is None:
            config = get_ai_config()
            provider = config.default_provider
        
        # Return cached instance if exists
        if provider in cls._instances:
            return cls._instances[provider]
        
        # Check if provider is registered
        if provider not in cls._PROVIDER_CLASSES:
            available = ", ".join(p.value for p in cls._PROVIDER_CLASSES.keys())
            raise ValueError(
                f"Provider '{provider.value}' not registered. "
                f"Available providers: {available}"
            )
        
        # Get provider configuration
        config_manager = AIConfigManager()
        provider_config = config_manager.get_provider_config(provider)
        
        if provider_config is None:
            raise ProviderNotConfiguredError(
                f"Provider '{provider.value}' is not configured. "
                f"Please set the required environment variables."
            )
        
        # Create provider instance
        try:
            provider_class = cls._PROVIDER_CLASSES[provider]
            provider_dict = {
                "api_key": provider_config.api_key,
                "api_url": provider_config.api_url,
                "timeout_seconds": provider_config.timeout_seconds,
                "max_retries": provider_config.max_retries,
                "retry_delay_seconds": provider_config.retry_delay_seconds,
                "enable_streaming": provider_config.enable_streaming,
            }
            
            instance = provider_class(provider_dict)
            cls._instances[provider] = instance
            
            logger.info(
                f"Created provider instance: {provider.value} "
                f"({provider_class.__name__})"
            )
            
            return instance
        
        except Exception as e:
            logger.error(
                f"Error creating provider '{provider.value}': {e}"
            )
            raise ProviderError(
                f"Failed to initialize provider '{provider.value}': {e}"
            )
    
    @classmethod
    def get_default_provider(cls) -> AIProvider:
        """
        Get the default provider instance.
        
        Returns:
            Default provider configured in settings
        """
        config = get_ai_config()
        return cls.get_provider(config.default_provider)
    
    @classmethod
    def get_available_providers(cls) -> Dict[AIProviderEnum, AIProvider]:
        """
        Get all available and configured providers.
        
        Only returns providers that are:
        1. Registered
        2. Configured with valid API keys
        3. Successfully instantiated
        
        Returns:
            Dictionary mapping provider enum to provider instance
            
        Example:
            ```python
            providers = ProviderFactory.get_available_providers()
            for provider_enum, provider in providers.items():
                print(f"Available: {provider_enum.value}")
            ```
        """
        available = {}
        config_manager = AIConfigManager()
        
        for provider in AIProviderEnum:
            try:
                if config_manager.is_provider_available(provider):
                    available[provider] = cls.get_provider(provider)
            except Exception as e:
                logger.warning(
                    f"Provider '{provider.value}' not available: {e}"
                )
        
        return available
    
    @classmethod
    def is_provider_available(cls, provider: AIProviderEnum) -> bool:
        """
        Check if a provider is available and configured.
        
        Args:
            provider: Provider to check
            
        Returns:
            True if provider can be used
        """
        try:
            config_manager = AIConfigManager()
            return config_manager.is_provider_available(provider)
        except Exception:
            return False
    
    @classmethod
    def switch_provider(
        cls,
        provider: AIProviderEnum
    ) -> AIProvider:
        """
        Switch to a different provider at runtime.
        
        Updates the default provider and returns its instance.
        
        Args:
            provider: Provider to switch to
            
        Returns:
            Provider instance
            
        Raises:
            ProviderNotConfiguredError: If provider not available
            
        Example:
            ```python
            # Switch to Anthropic
            provider = ProviderFactory.switch_provider(
                AIProviderEnum.ANTHROPIC
            )
            ```
        """
        if not cls.is_provider_available(provider):
            raise ProviderNotConfiguredError(
                f"Provider '{provider.value}' is not available"
            )
        
        # Update default
        config_manager = AIConfigManager()
        config_manager.set_default_provider(provider)
        
        logger.info(f"Switched to provider: {provider.value}")
        
        return cls.get_provider(provider)
    
    @classmethod
    def list_registered_providers(cls) -> list:
        """
        List all registered provider implementations.
        
        Returns:
            List of registered AIProviderEnum values
        """
        return list(cls._PROVIDER_CLASSES.keys())
    
    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear all cached provider instances.
        
        Useful for testing or when configuration changes at runtime.
        Next call to get_provider will create fresh instances.
        """
        cls._instances.clear()
        logger.info("Provider cache cleared")
    
    @classmethod
    def get_provider_info(cls, provider: AIProviderEnum) -> Dict[str, Any]:
        """
        Get information about a provider.
        
        Args:
            provider: Provider to get info for
            
        Returns:
            Dictionary with provider information
        """
        try:
            provider_instance = cls.get_provider(provider)
            models = provider_instance.get_available_models()
            
            return {
                "provider": provider.value,
                "available": True,
                "class": provider_instance.__class__.__name__,
                "models": [
                    {
                        "id": m.model_id,
                        "name": m.display_name,
                        "context_window": m.context_window,
                        "supports_vision": m.supports_vision,
                        "supports_function_calling": m.supports_function_calling,
                    }
                    for m in models
                ],
            }
        except Exception as e:
            return {
                "provider": provider.value,
                "available": False,
                "error": str(e),
            }
    
    @classmethod
    async def validate_all_providers(cls) -> Dict[AIProviderEnum, bool]:
        """
        Validate all configured providers.
        
        Makes test requests to each provider to verify they're working.
        Useful for health checks and monitoring.
        
        Returns:
            Dictionary mapping provider to validation result
        """
        results = {}
        
        for provider_enum, provider in cls.get_available_providers().items():
            try:
                is_valid = await provider.validate_api_key()
                results[provider_enum] = is_valid
                
                status = "✓ Valid" if is_valid else "✗ Invalid"
                logger.info(f"Provider {provider_enum.value}: {status}")
            
            except Exception as e:
                results[provider_enum] = False
                logger.error(
                    f"Error validating provider {provider_enum.value}: {e}"
                )
        
        return results


# Convenience functions for easy access

def get_provider(
    provider: Optional[AIProviderEnum] = None
) -> AIProvider:
    """
    Get a provider instance (convenience function).
    
    Args:
        provider: Provider enum or None for default
        
    Returns:
        Provider instance
        
    Example:
        ```python
        from app.ai.providers.factory import get_provider
        
        provider = get_provider()
        response = await provider.complete(request)
        ```
    """
    factory = ProviderFactory()
    return factory.get_provider(provider)


def get_default_provider() -> AIProvider:
    """
    Get the default configured provider.
    
    Returns:
        Default provider instance
    """
    factory = ProviderFactory()
    return factory.get_default_provider()


def get_available_providers() -> Dict[AIProviderEnum, AIProvider]:
    """
    Get all available providers.
    
    Returns:
        Dictionary of available providers
    """
    factory = ProviderFactory()
    return factory.get_available_providers()


def switch_provider(provider: AIProviderEnum) -> AIProvider:
    """
    Switch to a different provider.
    
    Args:
        provider: Provider to switch to
        
    Returns:
        Provider instance
    """
    factory = ProviderFactory()
    return factory.switch_provider(provider)
