from typing import List, Dict, Any, Callable

class ContextManager:
    """
    Implements Context-Folding strategy.
    Tracks token counts. At 8k tokens, escalated to OpenRouter to summarize the state
    into a 'Mission Manifest' and wipe the local Qwen buffer.
    """
    def __init__(self, token_limit: int = 8000):
        self.token_limit = token_limit
        self.current_tokens = 0
        self.message_buffer: List[Dict[str, str]] = []
        self.mission_manifest = ""

    def estimate_tokens(self, text: str) -> int:
        """Rough estimation: 1 token ~= 4 characters."""
        return len(text) // 4

    def add_message(self, role: str, content: str, openrouter_client: Callable):
        """Adds a message to the context buffer and checks for folding threshold."""
        self.message_buffer.append({"role": role, "content": content})
        self.current_tokens += self.estimate_tokens(content)

        if self.current_tokens >= self.token_limit:
            self._fold_context(openrouter_client)

    def _fold_context(self, openrouter_client: Callable):
        """
        Escalates to OpenRouter to generate a Mission Manifest, then wipes the buffer.
        """
        print("Context limit reached. Initiating Context-Folding...")
        # Prepare context for the Big Brain
        context_str = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in self.message_buffer])
        prompt = f"Summarize the following conversation state into a concise 'Mission Manifest':\\n{context_str}"

        # Call the Big Brain (OpenRouter)
        self.mission_manifest = openrouter_client(prompt)

        # Wipe the local Qwen buffer and start fresh with the manifest
        self.message_buffer = [{"role": "system", "content": f"Mission Manifest: {self.mission_manifest}"}]
        self.current_tokens = self.estimate_tokens(self.mission_manifest)
        print("Context folded successfully.")

    def get_context(self) -> List[Dict[str, str]]:
        return self.message_buffer
