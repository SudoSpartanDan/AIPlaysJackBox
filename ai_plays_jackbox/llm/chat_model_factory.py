from typing import Optional

from ai_plays_jackbox.llm.chat_model import ChatModel
from ai_plays_jackbox.llm.gemini_model import GeminiModel
from ai_plays_jackbox.llm.ollama_model import OllamaModel
from ai_plays_jackbox.llm.openai_model import OpenAIModel

CHAT_MODEL_PROVIDERS: dict[str, type[ChatModel]] = {
    "openai": OpenAIModel,
    "gemini": GeminiModel,
    "ollama": OllamaModel,
}


class ChatModelFactory:
    @staticmethod
    def get_chat_model(
        chat_model_provider: str,
        chat_model_name: Optional[str] = None,
        chat_model_temperature: float = 0.5,
        chat_model_top_p: float = 0.9,
    ) -> ChatModel:
        chat_model_provider = chat_model_provider.lower()
        if chat_model_provider not in CHAT_MODEL_PROVIDERS.keys():
            raise ValueError(f"Unknown chat model provider: {chat_model_provider}")

        return CHAT_MODEL_PROVIDERS[chat_model_provider](
            (
                chat_model_name
                if chat_model_name is not None
                else CHAT_MODEL_PROVIDERS[chat_model_provider].get_default_model()
            ),
            chat_model_temperature=chat_model_temperature,
            chat_model_top_p=chat_model_top_p,
        )
