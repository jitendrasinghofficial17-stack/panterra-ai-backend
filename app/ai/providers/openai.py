"""
OpenAI Provider Implementation

Implements the AIProvider interface for OpenAI's GPT models.
Supports GPT-4, GPT-4 Turbo, and GPT-3.5-Turbo with full feature parity.

Features:
- Text and vision completions
- Streaming responses
- Function calling (tools)
- Token counting
- Error handling and retry logic
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, List, AsyncGenerator
from datetime import datetime

import aiohttp
import requests

from app.ai.providers.base import (
    AIProvider,
    CompletionRequest,
    CompletionResponse,
    ModelInfo,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    TimeoutError as ProviderTimeoutError,
)

logger = logging.getLogger(__name__)


# OpenAI Model Information
OPENAI_MODELS = {
    "gpt-4-turbo-preview": ModelInfo(
        model_id="gpt-4-turbo-preview",
        provider="openai",
        display_name="GPT-4 Turbo",
        description="Most capable model, optimized for complex tasks",
        context_window=128000,
        max_output_tokens=4096,
        supports_vision=True,
        supports_function_calling=True,
        supports_streaming=True,
        cost_per_1k_input_tokens=0.01,
        cost_per_1k_output_tokens=0.03,
        release_date="2024-04-09",
        capabilities=[
            "text_completion",
            "vision",
            "function_calling",
            "streaming",
            "json_mode",
        ],
    ),
    "gpt-4": ModelInfo(
        model_id="gpt-4",
        provider="openai",
        display_name="GPT-4",
        description="Powerful model for complex reasoning",
        context_window=8192,
        max_output_tokens=2048,
        supports_vision=False,
        supports_function_calling=True,
        supports_streaming=True,
        cost_per_1k_input_tokens=0.03,
        cost_per_1k_output_tokens=0.06,
        release_date="2023-03-14",
        capabilities=[
            "text_completion",
            "function_calling",
            "streaming",
        ],
    ),
    "gpt-3.5-turbo": ModelInfo(
        model_id="gpt-3.5-turbo",
        provider="openai",
        display_name="GPT-3.5 Turbo",
        description="Fast and efficient model for most tasks",
        context_window=16385,
        max_output_tokens=4096,
        supports_vision=False,
        supports_function_calling=True,
        supports_streaming=True,
        cost_per_1k_input_tokens=0.0005,
        cost_per_1k_output_tokens=0.0015,
        release_date="2023-03-01",
        capabilities=[
            "text_completion",
            "function_calling",
            "streaming",
        ],
    ),
}


class OpenAIProvider(AIProvider):
    """
    OpenAI provider implementation for GPT models.
    
    Handles authentication, request formatting, response parsing,
    and error handling specific to OpenAI's API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dict with:
                - api_key: OpenAI API key
                - api_url: Base URL (default: https://api.openai.com/v1)
                - timeout_seconds: Request timeout
                - max_retries: Retry attempts
                - enable_streaming: Support streaming
        """
        super().__init__(config)
        self.api_url = self.api_url or "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "PANTERRA-AI/1.0",
        }
    
    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise AuthenticationError(
                "OPENAI_API_KEY is not set. "
                "Please set the API key in environment variables."
            )
        
        if not self.api_key.startswith("sk-"):
            logger.warning(
                "OpenAI API key does not start with 'sk-'. "
                "This may be invalid."
            )
    
    async def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key by making a test request.
        
        Returns:
            True if API key is valid
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(
                        total=self.timeout_seconds
                    ),
                ) as response:
                    if response.status == 401:
                        return False
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False
    
    async def complete(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """
        Generate text completion using OpenAI.
        
        Args:
            request: Completion request
            
        Returns:
            CompletionResponse with generated text
            
        Raises:
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
            ModelNotFoundError: If model not found
            ProviderTimeoutError: If request times out
            ProviderError: For other errors
        """
        # Format messages for OpenAI API
        if request.messages:
            messages = request.messages
        else:
            messages = self._format_messages(
                request.prompt,
                request.system_prompt
            )
        
        # Build request payload
        payload = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
        }
        
        # Add optional parameters if specified
        if request.top_k is not None:
            payload["top_k"] = request.top_k
        
        if request.frequency_penalty:
            payload["frequency_penalty"] = request.frequency_penalty
        
        if request.presence_penalty:
            payload["presence_penalty"] = request.presence_penalty
        
        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = "auto"
        
        # Execute request with retry logic
        response_data = await self._execute_with_retry(
            method="POST",
            endpoint="/chat/completions",
            payload=payload,
        )
        
        # Extract response data
        content = response_data["choices"][0]["message"]["content"]
        input_tokens = response_data["usage"]["prompt_tokens"]
        output_tokens = response_data["usage"]["completion_tokens"]
        finish_reason = response_data["choices"][0]["finish_reason"]
        
        # Log token usage
        self.log_completion_tokens(
            request.model,
            input_tokens,
            output_tokens
        )
        
        return CompletionResponse(
            content=content,
            model=request.model,
            provider="openai",
            tokens_used=input_tokens + output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
            raw_response=response_data,
            metadata={
                "completion_timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    async def stream(
        self,
        request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        """
        Stream text completion from OpenAI.
        
        Args:
            request: Completion request
            
        Yields:
            Text chunks as they're streamed
            
        Raises:
            ProviderError: For any errors
        """
        if not self.enable_streaming:
            raise ProviderError("Streaming is not enabled for this provider")
        
        # Format messages
        if request.messages:
            messages = request.messages
        else:
            messages = self._format_messages(
                request.prompt,
                request.system_prompt
            )
        
        # Build request payload
        payload = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "stream": True,
        }
        
        if request.frequency_penalty:
            payload["frequency_penalty"] = request.frequency_penalty
        
        if request.presence_penalty:
            payload["presence_penalty"] = request.presence_penalty
        
        # Create streaming request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(
                        total=self.timeout_seconds
                    ),
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    if response.status == 404:
                        raise ModelNotFoundError(
                            f"Model {request.model} not found"
                        )
                    if response.status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    if response.status >= 400:
                        raise ProviderError(
                            f"API error: {response.status}"
                        )
                    
                    # Stream response
                    async for line in response.content:
                        line = line.decode("utf-8").strip()
                        if not line or line == "data: [DONE]":
                            continue
                        if line.startswith("data: "):
                            try:
                                import json
                                data = json.loads(line[6:])
                                if "choices" in data:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except Exception as e:
                                logger.error(f"Error parsing stream: {e}")
                                continue
        
        except asyncio.TimeoutError:
            raise ProviderTimeoutError("Streaming request timed out")
        except aiohttp.ClientError as e:
            raise ProviderError(f"Streaming error: {e}")
    
    def get_model_info(self, model_id: str) -> ModelInfo:
        """
        Get information about an OpenAI model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            ModelInfo for the model
            
        Raises:
            ModelNotFoundError: If model not found
        """
        if model_id not in OPENAI_MODELS:
            raise ModelNotFoundError(
                f"OpenAI model '{model_id}' not found. "
                f"Available models: {list(OPENAI_MODELS.keys())}"
            )
        
        return OPENAI_MODELS[model_id]
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get all available OpenAI models."""
        return list(OPENAI_MODELS.values())
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_id: str,
    ) -> float:
        """
        Calculate cost of OpenAI completion.
        
        Args:
            input_tokens: Input token count
            output_tokens: Output token count
            model_id: Model used
            
        Returns:
            Cost in USD
        """
        try:
            model_info = self.get_model_info(model_id)
            input_cost = (input_tokens / 1000) * model_info.cost_per_1k_input_tokens
            output_cost = (output_tokens / 1000) * model_info.cost_per_1k_output_tokens
            return round(input_cost + output_cost, 6)
        except ModelNotFoundError:
            logger.warning(f"Model {model_id} not found for cost calculation")
            return 0.0
    
    # Private helper methods
    
    async def _execute_with_retry(
        self,
        method: str,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute API request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            payload: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            Various ProviderError subclasses based on error type
        """
        url = f"{self.api_url}{endpoint}"
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(
                            total=self.timeout_seconds
                        ),
                    ) as response:
                        response_data = await response.json()
                        
                        # Handle different status codes
                        if response.status == 200:
                            return response_data
                        elif response.status == 401:
                            raise AuthenticationError(
                                "Invalid OpenAI API key"
                            )
                        elif response.status == 404:
                            raise ModelNotFoundError(
                                f"Model not found: {response_data}"
                            )
                        elif response.status == 429:
                            raise RateLimitError(
                                "OpenAI rate limit exceeded"
                            )
                        elif response.status >= 500:
                            # Retry on server errors
                            last_error = ProviderError(
                                f"Server error: {response.status}"
                            )
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(
                                    self.retry_delay_seconds * (2 ** attempt)
                                )
                                continue
                        else:
                            raise ProviderError(
                                f"API error {response.status}: {response_data}"
                            )
            
            except asyncio.TimeoutError:
                last_error = ProviderTimeoutError(
                    f"Request timed out after {self.timeout_seconds}s"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(
                        self.retry_delay_seconds * (2 ** attempt)
                    )
                    continue
            
            except aiohttp.ClientError as e:
                last_error = ProviderError(f"Network error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(
                        self.retry_delay_seconds * (2 ** attempt)
                    )
                    continue
        
        if last_error:
            raise last_error
        
        raise ProviderError("Max retries exceeded")
    
    def _extract_text_from_response(
        self,
        response: Dict[str, Any]
    ) -> str:
        """Extract text from OpenAI response."""
        return response["choices"][0]["message"]["content"]
    
    def _extract_tokens_from_response(
        self,
        response: Dict[str, Any]
    ) -> tuple:
        """Extract token counts from OpenAI response."""
        return (
            response["usage"]["prompt_tokens"],
            response["usage"]["completion_tokens"],
        )
