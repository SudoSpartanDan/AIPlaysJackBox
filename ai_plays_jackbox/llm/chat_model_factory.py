from ai_plays_jackbox.llm.chat_model import ChatModel
from ai_plays_jackbox.llm.gemini_vertex_ai import GeminiVertextAIModel
from ai_plays_jackbox.llm.ollama_model import OllamaModel
from ai_plays_jackbox.llm.openai_model import OpenAIModel


class ChatModelFactory:
    @staticmethod
    def get_chat_model(
        chat_model_name: str,
        chat_model_temperature: float = 0.5,
        chat_model_top_p: float = 0.9,
    ) -> ChatModel:
        chat_model_name = chat_model_name.lower()
        if chat_model_name == "ollama":
            return OllamaModel(
                model="gemma3:12b", chat_model_temperature=chat_model_temperature, chat_model_top_p=chat_model_top_p
            )
        if chat_model_name == "openai":
            return OpenAIModel(
                model="gpt-4o-mini", chat_model_temperature=chat_model_temperature, chat_model_top_p=chat_model_top_p
            )
        if chat_model_name == "gemini":
            return GeminiVertextAIModel(
                model="gemini-2.0-flash-001",
                chat_model_temperature=chat_model_temperature,
                chat_model_top_p=chat_model_top_p,
            )
        else:
            raise ValueError(f"Unknown chat model type: {chat_model_name}")
