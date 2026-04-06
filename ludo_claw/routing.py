from enum import Enum
from typing import Dict, Any, Optional

class ModelTier(Enum):
    PRIMARY = "ollama/qwen3.5:9b"
    SECONDARY = "openrouter/claude-3.7"

class TaskComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Router:
    """
    Hybrid Model Routing for Ludo-Claw
    Primary (Ollama): Use Qwen 3.5 9B for standard tasks.
    Secondary (OpenRouter): Escalation trigger for high complexity or consecutive failures.
    """
    def __init__(self):
        self.consecutive_failures = 0
        self.MAX_FAILURES = 2

    def determine_model(self, task: Dict[str, Any], complexity: TaskComplexity) -> ModelTier:
        """
        Determines which model should be used based on task complexity and failure state.
        """
        if self.consecutive_failures >= self.MAX_FAILURES:
            print("Escalation Triggered: Consecutive failures threshold reached.")
            return ModelTier.SECONDARY

        if complexity == TaskComplexity.HIGH:
            print("Escalation Triggered: High complexity refactor identified by ULTRAPLAN.")
            return ModelTier.SECONDARY

        return ModelTier.PRIMARY

    def record_success(self):
        """Resets the failure counter on success."""
        self.consecutive_failures = 0

    def record_failure(self):
        """Increments the failure counter."""
        self.consecutive_failures += 1

    def get_current_state(self) -> Dict[str, Any]:
        return {
            "consecutive_failures": self.consecutive_failures,
            "escalated": self.consecutive_failures >= self.MAX_FAILURES
        }
