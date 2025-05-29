from typing import Optional

from loguru import logger
from ollama import Options, chat

from ai_plays_jackbox.llm import ChatModel


class OllamaModel(ChatModel):
    _model: str

    def __init__(self, model: str = "gemma3:12b"):
        self._model = model

    def generate_text(
        self,
        prompt: str,
        instructions: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.5,
        top_p: float = 0.9,
    ) -> str:
        instructions_formatted = {"role": "system", "content": instructions}
        chat_response = chat(
            model=self._model,
            messages=[instructions_formatted, {"role": "user", "content": prompt}],
            stream=False,
            options=Options(num_predict=max_tokens, temperature=temperature, top_p=top_p),
        )
        text = chat_response.message.content.strip().replace("\n", " ")
        logger.info(f"Generated text: {text}")
        return text
