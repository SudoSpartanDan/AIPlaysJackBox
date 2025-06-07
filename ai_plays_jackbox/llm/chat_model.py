from abc import ABC, abstractmethod
from typing import Optional


class ChatModel(ABC):
    _model: str
    _chat_model_temperature: float
    _chat_model_top_p: float

    def __init__(self, model: str, chat_model_temperature: float = 0.5, chat_model_top_p: float = 0.9):
        self._model = model
        self._chat_model_temperature = chat_model_temperature
        self._chat_model_top_p = chat_model_top_p

    @classmethod
    @abstractmethod
    def get_default_model(self) -> str:
        pass

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

    @abstractmethod
    def generate_sketch(
        self,
        prompt: str,
        instructions: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> bytes:
        pass
