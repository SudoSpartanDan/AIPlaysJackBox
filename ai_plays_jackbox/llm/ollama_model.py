from typing import Optional

from loguru import logger
from ollama import Options, chat, list

from ai_plays_jackbox.llm.chat_model import ChatModel


class OllamaModel(ChatModel):
    _model: str

    def __init__(self, model: str = "gemma3:12b", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = model

        # Check connection, this will hard fail if connection can't be made
        _ = list()

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
        text = chat_response.message.content.strip().replace("\n", " ")
        logger.info(f"Generated text: {text}")
        return text
