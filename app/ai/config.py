"""
AI Configuration Management

Centralized configuration for all AI providers, models, and behavior settings.
Supports environment-based overrides for different deployment environments.
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    LOCAL = "local"


class AIModel(str, Enum):
    """Supported AI models"""
    # OpenAI models
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Google Gemini models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    
    # Local models
    OLLAMA_LLAMA2 = "ollama:llama2"
    OLLAMA_MISTRAL = "ollama:mistral"


@dataclass
class ProviderConfig:
    """Configuration for a single AI provider"""
    provider: AIProvider
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    enable_streaming: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    model: AIModel
    provider: AIProvider
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    top_k: Optional[int] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIConfig:
    """Global AI configuration"""
    default_provider: AIProvider = AIProvider.OPENAI
    default_model: AIModel = AIModel.GPT_4_TURBO
    
    # Provider configs
    providers: Dict[AIProvider, ProviderConfig] = field(default_factory=dict)
    models: Dict[AIModel, ModelConfig] = field(default_factory=dict)
    
    # Feature flags
    enable_ai_features: bool = True
    enable_conversation_history: bool = True
    enable_memory_system: bool = True
    enable_tool_calling: bool = True
    enable_streaming_responses: bool = True
    
    # Performance settings
    conversation_history_limit: int = 50
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 60
    
    # Costs and monitoring
    track_token_usage: bool = True
    track_costs: bool = True
    log_all_requests: bool = False
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIConfigManager:
    """Manage AI configuration with environment variable support"""
    
    _instance: Optional['AIConfigManager'] = None
    _config: AIConfig = AIConfig()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from environment variables and defaults"""
        # Load default provider
        default_provider = os.getenv(
            "DEFAULT_AI_PROVIDER",
            AIProvider.OPENAI.value
        )
        self._config.default_provider = AIProvider(default_provider)
        
        # Load default model
        default_model = os.getenv(
            "DEFAULT_AI_MODEL",
            AIModel.GPT_4_TURBO.value
        )
        self._config.default_model = AIModel(default_model)
        
        # Load OpenAI configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self._config.providers[AIProvider.OPENAI] = ProviderConfig(
                provider=AIProvider.OPENAI,
                api_key=openai_key,
                api_url=os.getenv(
                    "OPENAI_API_URL",
                    "https://api.openai.com/v1"
                ),
                timeout_seconds=int(
                    os.getenv("OPENAI_TIMEOUT_SECONDS", "60")
                ),
                max_retries=int(
                    os.getenv("OPENAI_MAX_RETRIES", "3")
                ),
            )
        
        # Load Anthropic configuration
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self._config.providers[AIProvider.ANTHROPIC] = ProviderConfig(
                provider=AIProvider.ANTHROPIC,
                api_key=anthropic_key,
                api_url=os.getenv(
                    "ANTHROPIC_API_URL",
                    "https://api.anthropic.com"
                ),
                timeout_seconds=int(
                    os.getenv("ANTHROPIC_TIMEOUT_SECONDS", "120")
                ),
                max_retries=int(
                    os.getenv("ANTHROPIC_MAX_RETRIES", "3")
                ),
            )
        
        # Load Gemini configuration
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self._config.providers[AIProvider.GEMINI] = ProviderConfig(
                provider=AIProvider.GEMINI,
                api_key=gemini_key,
                api_url=os.getenv(
                    "GEMINI_API_URL",
                    "https://generativelanguage.googleapis.com/v1beta"
                ),
                timeout_seconds=int(
                    os.getenv("GEMINI_TIMEOUT_SECONDS", "60")
                ),
            )
        
        # Load Local/Ollama configuration
        ollama_url = os.getenv("OLLAMA_API_URL")
        if ollama_url:
            self._config.providers[AIProvider.LOCAL] = ProviderConfig(
                provider=AIProvider.LOCAL,
                api_url=ollama_url,
                timeout_seconds=int(
                    os.getenv("OLLAMA_TIMEOUT_SECONDS", "300")
                ),
            )
        
        # Load feature flags
        self._config.enable_ai_features = os.getenv(
            "ENABLE_AI_FEATURES",
            "true"
        ).lower() == "true"
        
        self._config.enable_conversation_history = os.getenv(
            "ENABLE_CONVERSATION_HISTORY",
            "true"
        ).lower() == "true"
        
        self._config.enable_memory_system = os.getenv(
            "ENABLE_MEMORY_SYSTEM",
            "true"
        ).lower() == "true"
        
        self._config.enable_tool_calling = os.getenv(
            "ENABLE_TOOL_CALLING",
            "true"
        ).lower() == "true"
        
        self._config.enable_streaming_responses = os.getenv(
            "ENABLE_STREAMING_RESPONSES",
            "true"
        ).lower() == "true"
        
        # Load performance settings
        self._config.conversation_history_limit = int(
            os.getenv("CONVERSATION_HISTORY_LIMIT", "50")
        )
        
        self._config.max_concurrent_requests = int(
            os.getenv("MAX_CONCURRENT_AI_REQUESTS", "100")
        )
        
        self._config.request_timeout_seconds = int(
            os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "60")
        )
        
        # Load monitoring settings
        self._config.track_token_usage = os.getenv(
            "TRACK_TOKEN_USAGE",
            "true"
        ).lower() == "true"
        
        self._config.track_costs = os.getenv(
            "TRACK_AI_COSTS",
            "true"
        ).lower() == "true"
        
        self._config.log_all_requests = os.getenv(
            "LOG_AI_REQUESTS",
            "false"
        ).lower() == "true"
    
    def get_config(self) -> AIConfig:
        """Get global AI configuration"""
        return self._config
    
    def get_provider_config(
        self,
        provider: AIProvider
    ) -> Optional[ProviderConfig]:
        """Get configuration for specific provider"""
        return self._config.providers.get(provider)
    
    def get_model_config(
        self,
        model: AIModel
    ) -> Optional[ModelConfig]:
        """Get configuration for specific model"""
        return self._config.models.get(model)
    
    def is_provider_available(
        self,
        provider: AIProvider
    ) -> bool:
        """Check if provider is available and configured"""
        provider_config = self._config.providers.get(provider)
        return provider_config is not None and provider_config.api_key is not None
    
    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return [
            provider
            for provider in self._config.providers.keys()
            if self.is_provider_available(provider)
        ]
    
    def set_default_provider(self, provider: AIProvider) -> None:
        """Set default AI provider"""
        if provider not in self._config.providers:
            raise ValueError(f"Provider {provider} not configured")
        self._config.default_provider = provider
    
    def set_default_model(self, model: AIModel) -> None:
        """Set default AI model"""
        if model not in self._config.models:
            raise ValueError(f"Model {model} not configured")
        self._config.default_model = model


# Singleton instance
ai_config = AIConfigManager()


def get_ai_config() -> AIConfig:
    """Get global AI configuration (dependency injection friendly)"""
    return ai_config.get_config()
