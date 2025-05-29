from abc import ABC, abstractmethod
from typing import Optional


class ChatModel(ABC):
    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        instructions: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.5,
        top_p: float = 0.9,
    ) -> str:
        pass
