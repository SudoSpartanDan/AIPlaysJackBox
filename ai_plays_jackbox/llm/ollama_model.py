from typing import Optional

from loguru import logger
from ollama import Options, chat, show

from ai_plays_jackbox.llm.chat_model import ChatModel


class OllamaModel(ChatModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Check connection and if model exists, this will hard fail if connection can't be made
        # Or if the model is not found
        _ = show(self._model)

    @classmethod
    def get_default_model(cls):
        return "gemma3:12b"

    def generate_text(
        self,
        prompt: str,
        instructions: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        if temperature is None:
            temperature = self._chat_model_temperature
        if top_p is None:
            top_p = self._chat_model_top_p

        instructions_formatted = {"role": "system", "content": instructions}
        chat_response = chat(
            model=self._model,
            messages=[instructions_formatted, {"role": "user", "content": prompt}],
            stream=False,
            options=Options(num_predict=max_tokens, temperature=temperature, top_p=top_p),
        )
        text = str(chat_response.message.content).strip().replace("\n", " ")
        logger.info(f"Generated text: {text}")
        return text

    def generate_sketch(
        self,
        prompt: str,
        instructions: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> bytes:
        raise Exception("Ollama model not supported yet for sketches")
