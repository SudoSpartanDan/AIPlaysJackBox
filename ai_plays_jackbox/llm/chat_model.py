from abc import ABC, abstractmethod
from typing import Optional


class ChatModel(ABC):
    _chat_model_temperature: float = 0.5
    _chat_model_top_p: float = 0.9

    def __init__(self, chat_model_temperature: float = 0.5, chat_model_top_p: float = 0.9):
        self._chat_model_temperature = chat_model_temperature
        self._chat_model_top_p = chat_model_top_p

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        instructions: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        pass
