from collections import deque
from typing import List, Dict


class ConversationMemory:
    """
    Sliding window conversation memory.
    Stores the last N user/assistant message pairs.
    """

    def __init__(self, window_size: int = 10):
        # window_size = total messages (user + assistant combined)
        self.window_size = window_size
        self.history: deque = deque(maxlen=window_size)

    def add(self, role: str, content: str):
        """Add a single message. Role is 'user' or 'assistant'."""
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        """Returns history as a list of {role, content} dicts."""
        return list(self.history)

    def clear(self):
        self.history.clear()

    def is_empty(self) -> bool:
        return len(self.history) == 0
    

class MemoryManager:
    """
    Manages per-session ConversationMemory instances.
    Acts as a registry — create, retrieve, and clear session memories.
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self._registry: Dict[str, ConversationMemory] = {}       # per-session conversation memory
                                                                 # format {"session_id": ConversationMemory}

    def get_or_create_memory(self, session_id: str) -> ConversationMemory:
        if session_id not in self._registry:
            self._registry[session_id] = ConversationMemory(
                window_size=self.window_size
            )
        return self._registry[session_id]

    def clear_session(self, session_id: str):
        if session_id in self._registry:
            self._registry[session_id].clear()

    def delete_session(self, session_id: str):
        """Fully removes a session from the registry."""
        self._registry.pop(session_id, None)

    def active_sessions(self) -> List[str]:
        return list(self._registry.keys())
