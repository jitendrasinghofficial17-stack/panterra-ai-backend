"""
AI Orchestration Package

Main orchestration layer for all AI operations.

Exports:
- AIOrchestrator: Main orchestration engine
- RequestPipeline: Request processing pipeline
- ResponsePipeline: Response processing pipeline
- create_orchestrator: Convenience factory function

Usage:
    from app.ai.orchestration import AIOrchestrator, create_orchestrator
    
    # Create orchestrator
    orchestrator = create_orchestrator(memory_manager)
    
    # Use for completions
    response = await orchestrator.complete(
        user_message="Hello!",
        user_id="user_123",
        conversation_id="conv_456"
    )
    
    # Use for streaming
    async for chunk in orchestrator.stream(
        user_message="Tell me a story",
        user_id="user_123",
        conversation_id="conv_456"
    ):
        print(chunk, end="")
"""

from app.ai.orchestration.orchestrator import (
    AIOrchestrator,
    OrchestratorError,
    create_orchestrator,
)

from app.ai.orchestration.request_pipeline import (
    RequestPipeline,
    RequestValidationError,
)

from app.ai.orchestration.response_pipeline import (
    ResponsePipeline,
    ResponseValidationError,
    ResponseProcessingError,
)

__all__ = [
    # Orchestrator
    "AIOrchestrator",
    "OrchestratorError",
    "create_orchestrator",
    
    # Request pipeline
    "RequestPipeline",
    "RequestValidationError",
    
    # Response pipeline
    "ResponsePipeline",
    "ResponseValidationError",
    "ResponseProcessingError",
]
